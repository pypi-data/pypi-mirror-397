use std::cmp::Ordering;
use std::collections::HashMap;
use std::fmt;

use chrono::{DateTime, Datelike, Duration, FixedOffset, NaiveDate, NaiveDateTime, NaiveTime};
use dicom_core::dictionary::DataDictionaryEntry;
use dicom_core::header::Header;
use dicom_core::{DataDictionary, DataElement, PrimitiveValue, Tag, VR};
use dicom_dictionary_std::StandardDataDictionary;
use dicom_object::mem::{InMemDicomObject, InMemElement};
use glob::Pattern;
use once_cell::sync::Lazy;
use rand::Rng;
use regex::Regex;
use serde::{Deserialize, Deserializer};
use serde_yaml::Value;
use sha2::{Digest, Sha256};
use smallvec::SmallVec;
use thiserror::Error;

use crate::dcm::parse::{DicomValue, get_dcm_value};
use crate::dcm::utils;

const PATIENT_BIRTH_DATE: Tag = Tag(0x0010, 0x0030);
const STUDY_DATE: Tag = Tag(0x0008, 0x0020);
const SERIES_DATE: Tag = Tag(0x0008, 0x0021);
const PATIENT_AGE: Tag = Tag(0x0010, 0x1010);
static DICOM_TAG_TUPLE_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"\(\s*([0-9a-fA-F]{4})\s*,\s*([0-9a-fA-F]{4})\s*\)").unwrap());

#[derive(Debug, Error)]
pub enum ProfileParseError {
    #[error("YAML parse error: {0}")]
    YamlError(String),

    #[error("Profile validation failed: {0:?}")]
    ValidationError(Vec<String>),

    #[error("Unsupported profile version: {0}")]
    UnsupportedVersion(u32),
}

#[derive(Debug, Clone)]
pub enum DeidProfile {
    V1(DeidProfileV1),
}

impl DeidProfile {
    pub fn from_yaml(yaml_data: &str) -> Result<DeidProfile, ProfileParseError> {
        let raw: Value = serde_yaml::from_str(yaml_data)
            .map_err(|e| ProfileParseError::YamlError(e.to_string()))?;
        let version = raw.get("version").and_then(|v| v.as_u64()).unwrap_or(1);
        match version {
            1 => {
                let v1: DeidProfileV1 = serde_yaml::from_value(raw)
                    .map_err(|e| ProfileParseError::YamlError(e.to_string()))?;
                Ok(DeidProfile::V1(v1))
            }
            v => Err(ProfileParseError::UnsupportedVersion(v as u32)),
        }
    }

    pub fn deid_dcm(&self, dcm: &[u8]) -> Result<Vec<u8>, String> {
        match self {
            DeidProfile::V1(profile) => profile.deid(dcm),
        }
    }

    pub fn matches_file_filter(&self, filename: &str) -> bool {
        match self {
            DeidProfile::V1(profile) => profile.matches_file_filter(filename),
        }
    }

    pub fn rename_file(&self, filename: &str, dcm_bytes: &[u8]) -> Result<Option<String>, String> {
        match self {
            DeidProfile::V1(profile) => profile.rename_file(filename, dcm_bytes),
        }
    }
}

#[derive(Debug, Deserialize, Clone)]
pub struct DeidProfileV1 {
    pub name: Option<String>,
    pub dicom: Option<DicomSectionV1>,
}

impl DeidProfileV1 {
    pub fn deid(&self, dcm: &[u8]) -> Result<Vec<u8>, String> {
        match self.dicom {
            Some(ref dicom) => dicom.deid(dcm),
            None => Ok(dcm.to_vec()),
        }
    }

    pub fn matches_file_filter(&self, filename: &str) -> bool {
        match &self.dicom {
            Some(dicom) => dicom.matches_file_filter(filename),
            None => true,
        }
    }

    pub fn rename_file(&self, filename: &str, dcm_bytes: &[u8]) -> Result<Option<String>, String> {
        match &self.dicom {
            Some(dicom) => dicom.rename_file(filename, dcm_bytes),
            None => Ok(None),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AgeUnit {
    Years,
    Months,
    Days,
}

impl<'de> Deserialize<'de> for AgeUnit {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        let s = String::deserialize(deserializer)?;
        match s.as_str() {
            "Y" | "y" => Ok(AgeUnit::Years),
            "M" | "m" => Ok(AgeUnit::Months),
            "D" | "d" => Ok(AgeUnit::Days),
            _ => Err(serde::de::Error::custom(format!("invalid age unit: {}", s))),
        }
    }
}

#[derive(Debug, Deserialize, Clone)]
pub struct FilenameRule {
    #[serde(rename = "input-regex")]
    pub input_regex: String,
    pub output: String,
}

#[derive(Debug, Deserialize, Clone)]
pub struct DicomSectionV1 {
    pub fields: Option<Vec<FieldSpecV1>>,
    pub filenames: Option<Vec<FilenameRule>>,
    #[serde(
        rename = "file-filter",
        deserialize_with = "deserialize_file_filter",
        default
    )]
    pub file_filter: Option<Vec<String>>,
    // global options
    #[serde(rename = "date-increment")]
    pub date_increment: Option<i64>,
    #[serde(rename = "date-format")]
    pub date_format: Option<String>,
    #[serde(rename = "datetime-format")]
    pub datetime_format: Option<String>,
    #[serde(rename = "jitter-date")]
    pub jitter_date: Option<bool>,
    #[serde(rename = "jitter-unit")]
    pub jitter_unit: Option<String>,
    #[serde(rename = "datetime-min")]
    pub datetime_min: Option<String>,
    #[serde(rename = "datetime-max")]
    pub datetime_max: Option<String>,
    #[serde(rename = "jitter-type")]
    pub jitter_type: Option<String>,
    #[serde(rename = "jitter-range")]
    pub jitter_range: Option<f64>,
    #[serde(rename = "patient-age-from-birthdate")]
    pub patient_age_from_birthdate: Option<bool>,
    #[serde(rename = "patient-age-units")]
    pub patient_age_units: Option<AgeUnit>,
    #[serde(rename = "recurse-sequence")]
    pub recurse_sequence: Option<bool>,
    #[serde(rename = "remove-private-tags")]
    pub remove_private_tags: Option<bool>,
    #[serde(rename = "remove-undefined")]
    pub remove_undefined: Option<bool>,
    #[serde(rename = "uid-prefix-fields")]
    pub uid_prefix_fields: Option<usize>,
    #[serde(rename = "uid-suffix-fields")]
    pub uid_suffix_fields: Option<usize>,
    #[serde(rename = "uid-numeric-name")]
    pub uid_numeric_name: Option<String>,
    #[serde(rename = "replace-with-insert")]
    pub replace_with_insert: Option<bool>,
    pub salt: Option<String>,
}

impl DicomSectionV1 {
    /// Check if a filename matches the file-filter patterns.
    /// Returns true if:
    /// - No file-filter is set (None), OR
    /// - The filename matches at least one of the patterns
    pub fn matches_file_filter(&self, filename: &str) -> bool {
        match &self.file_filter {
            None => true,
            Some(patterns) => {
                let filename_only = std::path::Path::new(filename)
                    .file_name()
                    .and_then(|s| s.to_str())
                    .unwrap_or(filename);

                patterns.iter().any(|pattern| {
                    Pattern::new(pattern)
                        .map(|p| p.matches(filename_only))
                        .unwrap_or(false)
                })
            }
        }
    }

    /// Rename a file based on filename rules
    pub fn rename_file(&self, filename: &str, dcm_bytes: &[u8]) -> Result<Option<String>, String> {
        let rules = match &self.filenames {
            Some(rules) if !rules.is_empty() => rules,
            _ => return Ok(None),
        };

        // extract just the filename (not the full path)
        let filename_only = std::path::Path::new(filename)
            .file_name()
            .and_then(|s| s.to_str())
            .unwrap_or(filename);

        for rule in rules {
            let re = Regex::new(&rule.input_regex)
                .map_err(|e| format!("Invalid input-regex '{}': {}", rule.input_regex, e))?;

            if let Some(captures) = re.captures(filename_only) {
                let cursor = std::io::Cursor::new(dcm_bytes);
                let obj = utils::from_reader_flexible(cursor)?;
                let mut substitutions = std::collections::HashMap::new();
                for name in re.capture_names().flatten() {
                    if let Some(value) = captures.name(name) {
                        substitutions.insert(name.to_string(), value.as_str().to_string());
                    }
                }
                let new_filename = substitute_template(&rule.output, &substitutions, &obj)?;
                return Ok(Some(new_filename));
            }
        }

        Ok(None)
    }

    pub fn deid(&self, dcm: &[u8]) -> Result<Vec<u8>, String> {
        // TODO collect errors and return them all at once
        let cursor = std::io::Cursor::new(dcm);
        let mut obj = utils::from_reader_flexible(cursor)?;

        if self.patient_age_from_birthdate.is_some() {
            set_patient_age_from_birth_date(&mut obj, self.patient_age_units)
                .map_err(|e| format!("Failed apply patient age from birthdate action: {e}"))?;
        }

        if self.remove_private_tags.unwrap_or(false) {
            let mut defined_private_tags: Vec<PrivateTag> = Vec::new();
            if let Some(ref fields) = self.fields {
                for field in fields {
                    if field.name.is_some() {
                        let fieldpaths = resolve_field_paths(&mut obj, field, false, None)?;
                        if fieldpaths.is_empty() {
                            continue;
                        }
                        // not nice but currently private tags always have one path with one item
                        if let Some(NestedItem::PrivateTag(tag)) = fieldpaths[0].first() {
                            defined_private_tags.push(tag.clone());
                        }
                    }
                }
            }
            remove_private_tags(&mut obj, &defined_private_tags);
        }

        let mut allowed_paths = Vec::new();

        if let Some(ref fields) = self.fields {
            let mut actions_by_path: HashMap<Vec<NestedItem>, Vec<&FieldSpecV1>> = HashMap::new();

            let paths_cache = if self.recurse_sequence.unwrap_or(false) {
                Some(utils::get_all_field_paths(&obj))
            } else {
                None
            };

            for field in fields.iter() {
                let fieldpaths = resolve_field_paths(
                    &mut obj,
                    field,
                    self.recurse_sequence.unwrap_or(false),
                    paths_cache.as_ref(),
                )?;
                if fieldpaths.is_empty() {
                    continue;
                }

                if self.remove_undefined.unwrap_or(false) {
                    allowed_paths.extend(fieldpaths.clone());
                }

                for path in fieldpaths {
                    if field.keep.unwrap_or(false) {
                        continue;
                    }
                    actions_by_path.entry(path).or_default().push(field);
                }
            }

            let options = ActionOptions {
                date_increment: self.date_increment,
                date_format: self.date_format.as_deref(),
                datetime_format: self.datetime_format.as_deref(),
                jitter_date: self.jitter_date,
                jitter_unit: self.jitter_unit.as_deref(),
                datetime_min: self.datetime_min.as_deref(),
                datetime_max: self.datetime_max.as_deref(),
                jitter_range: self.jitter_range,
                jitter_type: self.jitter_type.as_deref(),
                uid_prefix_fields: self.uid_prefix_fields,
                uid_suffix_fields: self.uid_suffix_fields,
                uid_numeric_name: self.uid_numeric_name.as_deref(),
                replace_with_insert: self.replace_with_insert,
                salt: self.salt.as_deref(),
            };
            apply_actions(&mut obj, &actions_by_path, &options)?;
        }

        if self.remove_undefined.unwrap_or(false) {
            remove_undefined_fields(&mut obj, &allowed_paths)?;
        }

        let mut out = Vec::new();
        obj.write_all(&mut out)
            .map_err(|e| format!("Failed to write DICOM: {e}"))?;
        Ok(out)
    }
}

#[derive(Debug, Deserialize, Clone)]
pub struct FieldSpecV1 {
    pub name: Option<String>,
    pub regex: Option<String>,
    pub remove: Option<bool>,
    #[serde(
        rename = "replace-with",
        deserialize_with = "empty_array_to_string",
        default
    )]
    pub replace_with: Option<String>,
    #[serde(rename = "replace-with-insert")]
    pub replace_with_insert: Option<bool>,
    pub hash: Option<bool>,
    #[serde(rename = "hashuid")]
    pub hash_uid: Option<bool>,
    #[serde(rename = "increment-date")]
    pub increment_date: Option<bool>,
    #[serde(rename = "increment-datetime")]
    pub increment_datetime: Option<bool>,
    #[serde(rename = "date-format")]
    pub date_format: Option<String>,
    #[serde(rename = "datetime-format")]
    pub datetime_format: Option<String>,
    #[serde(rename = "date-increment-override")]
    pub date_increment_override: Option<i64>,
    #[serde(rename = "jitter-date")]
    pub jitter_date: Option<bool>,
    #[serde(rename = "jitter-unit")]
    pub jitter_unit: Option<String>,
    #[serde(rename = "datetime-min")]
    pub datetime_min: Option<String>,
    #[serde(rename = "datetime-max")]
    pub datetime_max: Option<String>,
    pub jitter: Option<bool>,
    #[serde(rename = "jitter-type")]
    pub jitter_type: Option<String>,
    #[serde(rename = "jitter-range")]
    pub jitter_range: Option<f64>,
    #[serde(rename = "jitter-min")]
    pub jitter_min: Option<f64>,
    #[serde(rename = "jitter-max")]
    pub jitter_max: Option<f64>,
    pub keep: Option<bool>,
}

/// Options for applying de-identification actions
#[derive(Clone)]
struct ActionOptions<'a> {
    date_increment: Option<i64>,
    date_format: Option<&'a str>,
    datetime_format: Option<&'a str>,
    jitter_date: Option<bool>,
    jitter_unit: Option<&'a str>,
    datetime_min: Option<&'a str>,
    datetime_max: Option<&'a str>,
    jitter_range: Option<f64>,
    jitter_type: Option<&'a str>,
    uid_prefix_fields: Option<usize>,
    uid_suffix_fields: Option<usize>,
    uid_numeric_name: Option<&'a str>,
    replace_with_insert: Option<bool>,
    salt: Option<&'a str>,
}

fn resolve_field_paths(
    obj: &mut InMemDicomObject,
    field: &FieldSpecV1,
    recurse_sequence: bool,
    cache: Option<&Vec<String>>,
) -> Result<Vec<Vec<NestedItem>>, String> {
    if let Some(explicit_regex) = &field.regex {
        if recurse_sequence {
            return Err(
                "Sequence recursion is not supported when an explicit regex is specified."
                    .to_string(),
            );
        }
        return execute_regex_search(obj, explicit_regex, cache);
    }

    if let Some(name) = &field.name {
        if let Some(pattern) = utils::build_repeater_pattern(name, recurse_sequence) {
            return execute_regex_search(obj, &pattern, cache);
        } else {
            let mut fieldpaths = Vec::new();

            let initial_path = if let Some(captures) = DICOM_TAG_TUPLE_RE.captures(name) {
                format!(
                    "{}{}",
                    captures.get(1).unwrap().as_str(),
                    captures.get(2).unwrap().as_str()
                )
            } else {
                name.to_string()
            };

            let parsed_path = parse_nested_field(&initial_path)?;

            if recurse_sequence && parsed_path.len() > 1 {
                return Err("Sequence recursion not supported for pre-nested fields".to_string());
            }
            fieldpaths.push(parsed_path.clone());

            if recurse_sequence {
                if let Some(NestedItem::PrivateTag(tag)) = parsed_path.first() {
                    let private_paths = utils::get_private_tag_in_sequences(
                        obj,
                        tag.group,
                        tag.element,
                        &tag.creator,
                    );
                    for path in private_paths {
                        if path.ends_with(name) {
                            fieldpaths.push(parse_nested_field(&path)?);
                        }
                    }
                }

                // Use cached paths if available, otherwise fetch them (no clone!)
                let fetched_paths;
                let all_paths: &Vec<String> = if let Some(cached) = cache {
                    cached
                } else {
                    fetched_paths = utils::get_all_field_paths(obj);
                    &fetched_paths
                };

                for path in all_paths {
                    if path.ends_with(name) {
                        fieldpaths.push(parse_nested_field(path)?);
                    }
                }
            }

            return Ok(fieldpaths);
        }
    }

    Ok(Vec::new())
}

fn apply_actions(
    obj: &mut InMemDicomObject,
    actions_by_path: &std::collections::HashMap<Vec<NestedItem>, Vec<&FieldSpecV1>>,
    options: &ActionOptions,
) -> Result<(), String> {
    let mut top_lvl: Vec<(&Vec<NestedItem>, &Vec<&FieldSpecV1>)> = Vec::new();
    let mut sequences: HashMap<Tag, Vec<(&Vec<NestedItem>, &Vec<&FieldSpecV1>)>> = HashMap::new();

    for (path, field_ops) in actions_by_path.iter() {
        if path.len() == 1 {
            // Direct field access (no sequence)
            top_lvl.push((path, field_ops));
        } else if let Some(NestedItem::Tag(seq_tag)) = path.first() {
            // Sequence access - group by the sequence tag
            sequences
                .entry(*seq_tag)
                .or_default()
                .push((path, field_ops));
        } else {
            // Fallback for other cases
            top_lvl.push((path, field_ops));
        }
    }

    for (path, field_ops) in top_lvl {
        apply_to_path(obj, path, &|obj, tag| {
            apply_field_actions(obj, &tag, field_ops, options)
        })?;
    }

    for (seq_tag, paths_actions) in sequences.iter() {
        apply_sequence_actions(obj, *seq_tag, paths_actions, options)?;
    }

    Ok(())
}

fn apply_sequence_actions(
    obj: &mut InMemDicomObject,
    seq_tag: Tag,
    paths_actions: &Vec<(&Vec<NestedItem>, &Vec<&FieldSpecV1>)>,
    options: &ActionOptions,
) -> Result<(), String> {
    let elem = obj
        .element(seq_tag)
        .map_err(|e| format!("Tag {seq_tag:?} not found: {e}"))?;

    if let dicom_core::value::Value::Sequence(seq) = elem.value() {
        let mut items: Vec<InMemDicomObject> = seq.items().to_vec();

        for (path, field_ops) in paths_actions {
            if path.len() < 2 {
                continue;
            }

            let apply_actions = |obj: &mut InMemDicomObject, tag: NestedItem| {
                apply_field_actions(obj, &tag, field_ops, options)
            };

            match &path[1] {
                NestedItem::Index(idx) => {
                    if let Some(item) = items.get_mut(*idx) {
                        apply_to_path(item, &path[2..], &apply_actions)?;
                    }
                }
                NestedItem::Wildcard => {
                    for item in items.iter_mut() {
                        apply_to_path(item, &path[2..], &apply_actions)?;
                    }
                }
                _ => {}
            }
        }

        obj.put(DataElement::new(
            seq_tag,
            VR::SQ,
            dicom_core::value::DataSetSequence::<InMemDicomObject>::new(
                items,
                dicom_core::Length::UNDEFINED,
            ),
        ));
    }

    Ok(())
}

fn apply_field_actions(
    obj: &mut InMemDicomObject,
    tag: &NestedItem,
    field_ops: &Vec<&FieldSpecV1>,
    options: &ActionOptions,
) -> Result<(), String> {
    for field in field_ops {
        if field.remove.unwrap_or(false) {
            apply_remove(obj, tag).map_err(|e| format!("Failed to apply remove action: {e}"))?;
        } else if let Some(ref val) = field.replace_with {
            let insert = field
                .replace_with_insert
                .or(options.replace_with_insert)
                .unwrap_or(true);
            apply_replace_with(obj, tag, val, insert)
                .map_err(|e| format!("Failed to apply replace-with action: {e}"))?;
        } else if field.increment_date.unwrap_or(false) || field.increment_datetime.unwrap_or(false)
        {
            // Determine which date increment value to use (field override or global)
            let increment = field
                .date_increment_override
                .or(options.date_increment)
                .unwrap_or(0);

            // Determine the format to use (field-specific or global)
            // increment-date uses date-format, increment-datetime uses datetime-format
            let custom_format = if field.increment_datetime.unwrap_or(false) {
                field.datetime_format.as_deref().or(options.datetime_format)
            } else {
                field.date_format.as_deref().or(options.date_format)
            };

            // Determine jitter settings (field-specific or global)
            let jitter_date = field.jitter_date.or(options.jitter_date).unwrap_or(false);
            let jitter_unit = field
                .jitter_unit
                .as_deref()
                .or(options.jitter_unit)
                .unwrap_or("days");
            let jitter_range = options.jitter_range.unwrap_or(10.0) as i64;

            // Determine datetime min/max (field-specific or global) and parse them
            let datetime_min_str = field.datetime_min.as_deref().or(options.datetime_min);
            let datetime_max_str = field.datetime_max.as_deref().or(options.datetime_max);

            let datetime_min = datetime_min_str
                .map(|s| parse_datetime_minmax(s))
                .transpose()
                .map_err(|e| format!("Failed to parse datetime-min: {e}"))?;
            let datetime_max = datetime_max_str
                .map(|s| parse_datetime_minmax(s))
                .transpose()
                .map_err(|e| format!("Failed to parse datetime-max: {e}"))?;

            let action_name = if field.increment_datetime.unwrap_or(false) {
                "increment-datetime"
            } else {
                "increment-date"
            };

            apply_increment_date(
                obj,
                tag,
                increment,
                custom_format,
                jitter_date,
                jitter_unit,
                jitter_range,
                datetime_min,
                datetime_max,
            )
            .map_err(|e| format!("Failed to apply {action_name} action: {e}"))?;
        } else if field.hash.unwrap_or(false) {
            apply_hash(obj, tag, options.salt)
                .map_err(|e| format!("Failed to apply hash action: {e}"))?;
        } else if field.hash_uid.unwrap_or(false) {
            apply_hash_uid(
                obj,
                tag,
                options.uid_prefix_fields,
                options.uid_suffix_fields,
                options.uid_numeric_name,
                options.salt,
            )
            .map_err(|e| format!("Failed to apply hashuid action: {e}"))?;
        } else if field.jitter.unwrap_or(false) {
            let range = options.jitter_range.or(field.jitter_range).unwrap_or(2.0);
            let jitter_type_str = options
                .jitter_type
                .or(field.jitter_type.as_deref())
                .unwrap_or("float");
            apply_jitter(
                obj,
                tag,
                range,
                jitter_type_str,
                field.jitter_min,
                field.jitter_max,
            )
            .map_err(|e| format!("Failed to apply jitter action: {e}"))?;
        }
    }
    Ok(())
}

fn execute_regex_search(
    obj: &InMemDicomObject,
    pattern: &str,
    cache: Option<&Vec<String>>,
) -> Result<Vec<Vec<NestedItem>>, String> {
    let re =
        Regex::new(pattern).map_err(|e| format!("Invalid field regex '{}': {}", pattern, e))?;
    let fetched_paths;
    let all_paths: &Vec<String> = if let Some(cached) = cache {
        cached
    } else {
        fetched_paths = utils::get_all_field_paths(obj);
        &fetched_paths
    };

    all_paths
        .iter()
        .filter(|path| re.is_match(path))
        .map(|path| parse_nested_field(path))
        .collect()
}

fn apply_to_path<F>(obj: &mut InMemDicomObject, path: &[NestedItem], f: &F) -> Result<(), String>
where
    F: Fn(&mut InMemDicomObject, NestedItem) -> Result<(), String>,
{
    if path.is_empty() {
        return Ok(());
    }

    match &path[0] {
        NestedItem::PrivateTag { .. } => {
            if path.len() == 1 {
                return f(obj, path[0].clone());
            }
            Err("Path must start with a tag".to_string())
        }
        NestedItem::Tag(tag) => {
            if path.len() == 1 {
                return f(obj, path[0].clone());
            }

            let is_sequence = obj
                .element(*tag)
                .map(|elem| matches!(elem.value(), dicom_core::value::Value::Sequence(_)))
                .unwrap_or(false);

            if !is_sequence {
                return Ok(());
            }

            if let Ok(elem) = obj.element(*tag)
                && let dicom_core::value::Value::Sequence(seq) = elem.value()
            {
                let mut items: Vec<InMemDicomObject> = seq.items().to_vec();

                match &path[1] {
                    NestedItem::Index(idx) => {
                        if let Some(target) = items.get_mut(*idx) {
                            apply_to_path(target, &path[2..], f)?;
                        }
                    }
                    NestedItem::Wildcard => {
                        // Modify all items
                        for item in items.iter_mut() {
                            apply_to_path(item, &path[2..], f)?;
                        }
                    }
                    NestedItem::Tag(_) => {
                        return Err("Expected sequence index but found tag".to_string());
                    }
                    NestedItem::PrivateTag { .. } => {
                        return Err("Expected sequence index but found private tag".to_string());
                    }
                }

                obj.put(DataElement::new(
                    *tag,
                    VR::SQ,
                    dicom_core::value::DataSetSequence::<InMemDicomObject>::new(
                        items,
                        dicom_core::Length::UNDEFINED,
                    ),
                ));
            }
            Ok(())
        }
        _ => Err("Path must start with a tag".to_string()),
    }
}

pub fn apply_remove(
    obj: &mut InMemDicomObject,
    item: &NestedItem,
) -> Result<(), Box<dyn std::error::Error>> {
    if let Some(tag) = resolve_tag(obj, item)? {
        obj.remove_element(tag);
    }
    Ok(())
}

pub fn apply_replace_with(
    obj: &mut InMemDicomObject,
    item: &NestedItem,
    new_text: &str,
    insert: bool,
) -> Result<(), Box<dyn std::error::Error>> {
    if let Some(tag) = resolve_tag(obj, item)? {
        let vr = match obj.element(tag) {
            Ok(el) => el.header().vr(),
            Err(_) => {
                if !insert {
                    // Field does not exist and insert is false, skip
                    return Ok(());
                }
                resolve_vr(item).map_err(|e| format!("{tag}: {e}"))?
            }
        };
        let new_value = validate_vr_value(vr, new_text).map_err(|e| format!("{tag}: {e}"))?;
        obj.put(DataElement::new(tag, vr, new_value));
    } else if let NestedItem::PrivateTag(tag) = item {
        // Check if private tag exists
        let exists = obj
            .private_element(tag.group, &tag.creator, tag.element)
            .is_ok();
        if !exists && !insert {
            // Field does not exist and insert is false, skip
            return Ok(());
        }
        let vr = resolve_vr(item).map_err(|e| format!("{tag}: {e}"))?;
        let new_value = validate_vr_value(vr, new_text).map_err(|e| format!("{tag}: {e}"))?;
        obj.put_private_element(tag.group, &tag.creator, tag.element, vr, new_value)?;
    }
    Ok(())
}

pub fn apply_increment_date(
    obj: &mut InMemDicomObject,
    item: &NestedItem,
    increment: i64,
    custom_format: Option<&str>,
    jitter_date: bool,
    jitter_unit: &str,
    jitter_range: i64,
    datetime_min: Option<DateTime<FixedOffset>>,
    datetime_max: Option<DateTime<FixedOffset>>,
) -> Result<(), Box<dyn std::error::Error>> {
    if let Some(tag) = resolve_tag(obj, item)? {
        let vr = match obj.element(tag) {
            Ok(el) => el.header().vr(),
            Err(_) => return Ok(()),
        };
        let value = get_dcm_value(obj, tag).map_err(|e| format!("{tag}: {e}"))?;
        if matches!(value, DicomValue::Empty) {
            return Ok(());
        }

        let value_str = value.to_string();

        // Check if the value contains commas (multi-value)
        if value_str.contains(',') {
            // Process each value separately
            let values: Vec<&str> = value_str.split(',').collect();
            let mut new_value_parts = Vec::new();

            for val in values {
                let inc_value = increment_date(
                    &vr.to_string(),
                    val.trim(),
                    increment,
                    custom_format,
                    jitter_date,
                    jitter_unit,
                    jitter_range,
                    datetime_min,
                    datetime_max,
                )
                .map_err(|e| format!("{tag}: {e}"))?;

                // Validate each part individually
                let validated =
                    validate_vr_value(vr, &inc_value).map_err(|e| format!("{tag}: {e}"))?;
                new_value_parts.push(validated);
            }

            // Combine validated values into a multi-value element
            let combined_value = if new_value_parts.len() == 1 {
                new_value_parts.into_iter().next().unwrap()
            } else {
                // Build multi-value from individual strings
                let all_strings: Vec<String> = new_value_parts
                    .into_iter()
                    .flat_map(|v| v.to_multi_str().into_owned())
                    .collect();
                PrimitiveValue::Strs(all_strings.into())
            };
            obj.put(DataElement::new(tag, vr, combined_value));
        } else {
            let new_value_str = increment_date(
                &vr.to_string(),
                &value_str,
                increment,
                custom_format,
                jitter_date,
                jitter_unit,
                jitter_range,
                datetime_min,
                datetime_max,
            )
            .map_err(|e| format!("{tag}: {e}"))?;

            let new_value =
                validate_vr_value(vr, &new_value_str).map_err(|e| format!("{tag}: {e}"))?;
            obj.put(DataElement::new(tag, vr, new_value));
        }
    }
    Ok(())
}

pub fn apply_hash(
    obj: &mut InMemDicomObject,
    item: &NestedItem,
    salt: Option<&str>,
) -> Result<(), Box<dyn std::error::Error>> {
    if let Some(tag) = resolve_tag(obj, item)? {
        let vr = match obj.element(tag) {
            Ok(el) => el.header().vr(),
            Err(_) => return Ok(()),
        };
        let value = get_dcm_value(obj, tag).map_err(|e| format!("{tag}: {e}"))?;
        if matches!(value, DicomValue::Empty) {
            return Ok(());
        }
        let hashed_value = hash(&value.to_string(), Some("hex"), salt);
        let new_value =
            validate_vr_value(vr, &hashed_value[..16]).map_err(|e| format!("{tag}: {e}"))?;
        obj.put(DataElement::new(tag, vr, new_value));
    }
    Ok(())
}

pub fn apply_hash_uid(
    obj: &mut InMemDicomObject,
    item: &NestedItem,
    uid_prefix_fields: Option<usize>,
    uid_suffix_fields: Option<usize>,
    uid_numeric_name: Option<&str>,
    salt: Option<&str>,
) -> Result<(), Box<dyn std::error::Error>> {
    if let Some(tag) = resolve_tag(obj, item)? {
        let vr = match obj.element(tag) {
            Ok(el) => el.header().vr(),
            Err(_) => return Ok(()),
        };
        let value = get_dcm_value(obj, tag).map_err(|e| format!("{tag}: {e}"))?;
        if matches!(value, DicomValue::Empty) {
            return Ok(());
        }
        let value_str = value.to_string();
        let hashed_value = hash_uid(
            &value_str,
            uid_prefix_fields,
            uid_suffix_fields,
            uid_numeric_name,
            salt,
        )?;
        let new_value = validate_vr_value(vr, &hashed_value).map_err(|e| format!("{tag}: {e}"))?;
        obj.put(DataElement::new(tag, vr, new_value));
    }
    Ok(())
}

pub fn apply_jitter(
    obj: &mut InMemDicomObject,
    item: &NestedItem,
    jitter_range: f64,
    jitter_type: &str,
    jitter_min: Option<f64>,
    jitter_max: Option<f64>,
) -> Result<(), Box<dyn std::error::Error>> {
    if let Some(tag) = resolve_tag(obj, item)? {
        let vr = match obj.element(tag) {
            Ok(el) => el.header().vr(),
            Err(_) => return Ok(()),
        };
        let value = get_dcm_value(obj, tag).map_err(|e| format!("{tag}: {e}"))?;
        if matches!(value, DicomValue::Empty) {
            return Ok(());
        }
        let mut new_value = match value {
            DicomValue::Int(value) => jitter(
                value as f64,
                jitter_range,
                jitter_type,
                jitter_min,
                jitter_max,
            )?,
            DicomValue::Float(value) => {
                jitter(value, jitter_range, jitter_type, jitter_min, jitter_max)?
            }
            _ => return Err(format!("{tag}: Unsupported value type for jittering").into()),
        };
        match vr {
            VR::IS | VR::UL | VR::US => {
                if jitter_type == "float" {
                    new_value = new_value.floor();
                }
                let (min, max) = match vr {
                    VR::US => (0.0, (2u32.pow(16) - 1) as f64),
                    VR::UL => (0.0, (2u32.pow(32) - 1) as f64),
                    _ => (f64::MIN, f64::MAX),
                };
                new_value = new_value.clamp(min, max);
            }
            _ => {}
        }
        let formatted = match vr {
            VR::US | VR::UL | VR::IS => format!("{}", new_value as u64),
            VR::FL | VR::FD => format!("{}", new_value),
            _ => new_value.to_string(),
        };
        let new_value = validate_vr_value(vr, &formatted).map_err(|e| format!("{tag}: {e}"))?;
        obj.put(DataElement::new(tag, vr, new_value));
    }
    Ok(())
}

fn resolve_tag(
    obj: &InMemDicomObject,
    item: &NestedItem,
) -> Result<Option<Tag>, Box<dyn std::error::Error>> {
    match item {
        NestedItem::Tag(tag) => Ok(Some(*tag)),
        NestedItem::PrivateTag(tag) => {
            if let Ok(private_el) = obj.private_element(tag.group, &tag.creator, tag.element) {
                Ok(Some(private_el.tag()))
            } else {
                Ok(None)
            }
        }
        _ => Err("Nested item must be a tag".into()),
    }
}

fn resolve_vr(item: &NestedItem) -> Result<VR, String> {
    match item {
        NestedItem::Tag(tag) => {
            if let Some(entry) = StandardDataDictionary.by_tag(*tag) {
                let vvr = entry.vr();
                Ok(vvr.exact().unwrap_or_else(|| vvr.relaxed()))
            } else {
                Ok(VR::UN)
            }
        }
        NestedItem::PrivateTag(tag) => {
            match utils::get_private_tag_vr(tag.group, tag.element, &tag.creator) {
                Some(vr) => Ok(vr),
                _ => Err("Could not resolve VR for private tag".to_string()),
            }
        }
        _ => Err("Item must be a tag".into()),
    }
}

fn validate_vr_value(vr: VR, value: &str) -> Result<PrimitiveValue, String> {
    if value.is_empty() {
        return Ok(PrimitiveValue::Empty);
    }

    match vr {
        VR::DA => {
            NaiveDate::parse_from_str(value, "%Y%m%d")
                .map_err(|_| format!("{value} cannot be parsed as DA"))?;
            Ok(PrimitiveValue::from(value.to_string()))
        }

        VR::TM => {
            let fmts = ["%H", "%H%M", "%H%M%S", "%H%M%S%.f"];
            if !fmts
                .iter()
                .any(|f| NaiveTime::parse_from_str(value, f).is_ok())
            {
                return Err(format!("{value} cannot be parsed as TM"));
            }
            Ok(PrimitiveValue::from(value.to_string()))
        }

        VR::DT => {
            let fmts = [
                "%Y%m%d%H%M%S",
                "%Y%m%d%H%M%S%.f",
                "%Y%m%d%H%M",
                "%Y%m%d%H",
                "%Y%m%d",
            ];
            if !fmts
                .iter()
                .any(|f| NaiveDateTime::parse_from_str(value, f).is_ok())
            {
                return Err(format!("{value} cannot be parsed as DT"));
            }
            Ok(PrimitiveValue::from(value.to_string()))
        }

        VR::DS => {
            let vals: Result<Vec<f64>, _> =
                value.split('\\').map(|v| v.trim().parse::<f64>()).collect();
            match vals {
                Ok(nums) => Ok(PrimitiveValue::F64(SmallVec::from_vec(nums))),
                Err(_) => Err(format!("{value} cannot be parsed as {vr:?}")),
            }
        }

        VR::FL => {
            let vals: Result<Vec<f32>, _> =
                value.split('\\').map(|v| v.trim().parse::<f32>()).collect();
            match vals {
                Ok(nums) => Ok(PrimitiveValue::F32(SmallVec::from_vec(nums))),
                Err(_) => Err(format!("{value} cannot be parsed as {vr:?}")),
            }
        }

        VR::FD => {
            let vals: Result<Vec<f64>, _> =
                value.split('\\').map(|v| v.trim().parse::<f64>()).collect();
            match vals {
                Ok(nums) => Ok(PrimitiveValue::F64(SmallVec::from_vec(nums))),
                Err(_) => Err(format!("{value} cannot be parsed as {vr:?}")),
            }
        }

        VR::IS => {
            let vals: Result<Vec<i64>, _> =
                value.split('\\').map(|v| v.trim().parse::<i64>()).collect();
            match vals {
                Ok(nums) => Ok(PrimitiveValue::I64(SmallVec::from_vec(nums))),
                Err(_) => Err(format!("{value} cannot be parsed as {vr:?}")),
            }
        }

        VR::UL => {
            let vals: Result<Vec<u32>, _> =
                value.split('\\').map(|v| v.trim().parse::<u32>()).collect();
            match vals {
                Ok(nums) => Ok(PrimitiveValue::U32(SmallVec::from_vec(nums))),
                Err(_) => Err(format!("{value} cannot be parsed as {vr:?}")),
            }
        }
        VR::SL => {
            let vals: Result<Vec<i32>, _> =
                value.split('\\').map(|v| v.trim().parse::<i32>()).collect();
            match vals {
                Ok(nums) => Ok(PrimitiveValue::I32(SmallVec::from_vec(nums))),
                Err(_) => Err(format!("{value} cannot be parsed as {vr:?}")),
            }
        }
        VR::SS => {
            let vals: Result<Vec<i16>, _> =
                value.split('\\').map(|v| v.trim().parse::<i16>()).collect();
            match vals {
                Ok(nums) => Ok(PrimitiveValue::I16(SmallVec::from_vec(nums))),
                Err(_) => Err(format!("{value} cannot be parsed as {vr:?}")),
            }
        }
        VR::US => {
            let vals: Result<Vec<u16>, _> =
                value.split('\\').map(|v| v.trim().parse::<u16>()).collect();
            match vals {
                Ok(nums) => Ok(PrimitiveValue::U16(SmallVec::from_vec(nums))),
                Err(_) => Err(format!("{value} cannot be parsed as {vr:?}")),
            }
        }

        _ => Ok(PrimitiveValue::from(value.to_string())),
    }
}

pub fn hash(message: &str, format: Option<&str>, salt: Option<&str>) -> String {
    let mut hasher = Sha256::new();
    if let Some(salt_value) = salt {
        hasher.update(salt_value.as_bytes());
    }
    hasher.update(message.as_bytes());
    let result = hasher.finalize();
    match format.unwrap_or("hex") {
        "dec" => result.iter().map(|b| b.to_string()).collect(),
        _ => hex::encode(result),
    }
}

const UID_PREFIX_FIELDS: usize = 4;
const UID_SUFFIX_FIELDS: usize = 1;
const UID_HASH_FIELDS: [usize; 6] = [6, 6, 6, 6, 6, 6];
const UID_MAX_SUFFIX_DIGITS: usize = 6;
const UID_MAX_LENGTH: usize = 64;

pub fn hash_uid(
    value: &str,
    uid_prefix_fields: Option<usize>,
    uid_suffix_fields: Option<usize>,
    uid_numeric_name: Option<&str>,
    salt: Option<&str>,
) -> Result<String, Box<dyn std::error::Error>> {
    let original_parts: Vec<&str> = value.split('.').collect();
    let prefix_fields = uid_prefix_fields.unwrap_or(UID_PREFIX_FIELDS);
    let suffix_fields = uid_suffix_fields.unwrap_or(UID_SUFFIX_FIELDS);

    // determine how many fields are required
    if uid_numeric_name.is_none() {
        let required = prefix_fields + suffix_fields;
        if required > original_parts.len() {
            return Err("UID is too short to be hashed".into());
        }
    }

    // get the digest
    let decimal_digest = hash(value, Some("dec"), salt);
    let mut result_parts: Vec<String> = Vec::new();

    // build the new UID string with prefix
    if prefix_fields > 0 {
        if let Some(numeric_name) = uid_numeric_name {
            let numeric_parts: Vec<&str> = numeric_name.split('.').collect();
            if numeric_parts.len() != prefix_fields {
                return Err(format!(
                    "Registered OID numeric name must have exactly {} fields",
                    prefix_fields
                )
                .into());
            }
            result_parts.extend(numeric_parts.iter().map(|s| s.to_string()));
        } else {
            result_parts.extend(
                original_parts
                    .iter()
                    .take(prefix_fields)
                    .map(|s| s.to_string()),
            );
        }
    }

    // parts taken from hash string
    let mut index = 0;
    for &segment_len in UID_HASH_FIELDS.iter() {
        let end = usize::min(index + segment_len, decimal_digest.len());
        let mut part = decimal_digest[index..end].to_string();
        // DICOM UID block cannot start with 0, replacing by 1
        if part.starts_with('0') {
            part = format!("1{}", &part[1..]);
        }
        result_parts.push(part);
        index += segment_len;
    }

    if suffix_fields > 0 {
        let mut suffix = Vec::new();
        // keep no more than the number of digits specified
        let start_idx = if suffix_fields > original_parts.len() {
            0
        } else {
            original_parts.len() - suffix_fields
        };

        for part in &original_parts[start_idx..] {
            let mut part_str = part.to_string();
            if part_str.len() > UID_MAX_SUFFIX_DIGITS {
                let from_index = part_str.len() - UID_MAX_SUFFIX_DIGITS;
                part_str = part_str[from_index..].to_string();
            }
            suffix.push(part_str);
        }
        result_parts.extend(suffix);
    }

    let mut new_value = result_parts.join(".");
    if new_value.len() > UID_MAX_LENGTH {
        let parts: Vec<String> = new_value.split('.').map(|s| s.to_string()).collect();
        let mut rest = parts[..parts.len() - 1].to_vec();
        let suffix = parts[parts.len() - 1].clone();

        while rest
            .iter()
            .chain(std::iter::once(&suffix))
            .map(|s| s.len() + 1)
            .sum::<usize>()
            - 1
            > UID_MAX_LENGTH
        {
            if let Some(last) = rest.last_mut() {
                if last.len() > 1 {
                    last.truncate(last.len() - 1);
                } else {
                    rest.pop();
                }
            } else {
                break;
            }
        }

        rest.push(suffix);
        new_value = rest.join(".");
    }

    Ok(new_value)
}

fn parse_datetime_minmax(value: &str) -> Result<DateTime<FixedOffset>, String> {
    // Check if it's a relative date (e.g., "-80years", "+30days")
    let re = regex::Regex::new(r"^(?P<direction>[+-])(?P<amount>\d+)(?P<unit>years|weeks|days)$")
        .unwrap();

    if let Some(caps) = re.captures(value) {
        let direction = &caps["direction"];
        let amount: i64 = caps["amount"]
            .parse()
            .map_err(|e| format!("Invalid amount: {e}"))?;
        let unit = &caps["unit"];

        let now = chrono::Local::now().with_timezone(&FixedOffset::east_opt(0).unwrap());
        let delta = match unit {
            "years" => Duration::days((amount as f64 * 365.25) as i64),
            "weeks" => Duration::weeks(amount),
            "days" => Duration::days(amount),
            _ => return Err(format!("Unsupported unit: {unit}")),
        };

        let result = if direction == "-" {
            now - delta
        } else {
            now + delta
        };

        Ok(result)
    } else {
        // Try parsing as fixed date in YYYYMMDD format
        NaiveDate::parse_from_str(value, "%Y%m%d")
            .map(|d| {
                d.and_hms_opt(0, 0, 0)
                    .unwrap()
                    .and_local_timezone(FixedOffset::east_opt(0).unwrap())
                    .unwrap()
            })
            .map_err(|_| {
                format!(
                    "datetime-min/datetime-max must be in either yyyymmdd or [+-]<amount><unit> format. \
                    Value {value} is unable to be parsed."
                )
            })
    }
}

fn increment_date(
    vr: &str,
    value: &str,
    increment: i64,
    custom_format: Option<&str>,
    jitter_date: bool,
    jitter_unit: &str,
    jitter_range: i64,
    datetime_min: Option<DateTime<FixedOffset>>,
    datetime_max: Option<DateTime<FixedOffset>>,
) -> Result<String, String> {
    if value.is_empty() {
        return Ok(value.to_string());
    }
    // Determine the format to use for parsing and output
    // For parsing: use custom format if specified, otherwise use VR default
    let parse_fmt = if let Some(cf) = custom_format {
        cf
    } else {
        match vr {
            "DA" => "%Y%m%d",
            "DT" => "%Y%m%d%H%M%S.%f",
            _ => "%Y%m%d",
        }
    };
    // For output: use VR default for DA/DT (to maintain DICOM compliance), custom for others
    let output_fmt = match vr {
        "DA" => "%Y%m%d",
        "DT" => "%Y%m%d%H%M%S.%f",
        _ => custom_format.unwrap_or("%Y%m%d"),
    };
    // Extract and preserve timezone suffix if present (only for non-timestamp formats)
    let mut suffix = String::new();
    let mut parse_value = value;

    if parse_fmt != "timestamp" && vr == "DT" && value.len() > 5 {
        let last_5 = &value[value.len() - 5..];
        if last_5.starts_with('+') || last_5.starts_with('-') {
            parse_value = &value[..value.len() - 5];
            suffix = last_5.to_string();
        }
    }
    // Add fractional seconds if format expects them but they're not present
    let mut adjusted_parse_value = parse_value.to_string();
    if parse_fmt.ends_with(".%f") && !parse_value.contains('.') {
        adjusted_parse_value.push_str(".0");
    }
    // Parse the date based on format
    let dt = if parse_fmt == "timestamp" {
        // Special handling for timestamp format
        let timestamp = adjusted_parse_value
            .parse::<f64>()
            .map_err(|e| format!("Unable to parse timestamp: {e}"))?;
        DateTime::from_timestamp(
            timestamp as i64,
            (timestamp.fract() * 1_000_000_000.0) as u32,
        )
        .ok_or_else(|| format!("Invalid timestamp: {timestamp}"))?
        .fixed_offset()
    } else {
        // Parse using the specified format string
        let naive = NaiveDateTime::parse_from_str(&adjusted_parse_value, parse_fmt)
            .or_else(|_| {
                // Try parsing as just a date if datetime parsing fails
                NaiveDate::parse_from_str(&adjusted_parse_value, parse_fmt)
                    .map(|d| d.and_hms_opt(0, 0, 0).unwrap())
            })
            .map_err(|e| format!("Unable to parse date field with format {parse_fmt}: {e}"))?;

        // Convert to DateTime with UTC offset
        naive
            .and_local_timezone(FixedOffset::east_opt(0).unwrap())
            .single()
            .ok_or_else(|| "Failed to convert to fixed offset".to_string())?
    };

    // Calculate the total increment with optional jitter
    let mut total_increment = Duration::days(increment);
    if jitter_date {
        let mut rng = rand::rng();
        let rand_val: i64 = loop {
            let rv = rng.random_range(-jitter_range..=jitter_range);
            if rv != 0 {
                break rv;
            }
        };
        // Add jitter based on unit
        let jitter_duration = match jitter_unit {
            "years" => Duration::days((rand_val as f64 * 365.25) as i64),
            "weeks" => Duration::weeks(rand_val),
            "days" => Duration::days(rand_val),
            _ => Duration::days(rand_val), // default to days
        };

        total_increment = total_increment + jitter_duration;
    }
    // Apply the increment
    let mut adjusted = dt + total_increment;
    // Apply min/max bounds if specified
    if let Some(min_dt) = datetime_min {
        if adjusted < min_dt {
            adjusted = min_dt;
        }
    }
    if let Some(max_dt) = datetime_max {
        if adjusted > max_dt {
            adjusted = max_dt;
        }
    }
    // Format the result using the output format
    let result = if parse_fmt == "timestamp" {
        // Output as timestamp
        let timestamp = adjusted.timestamp() as f64
            + (adjusted.timestamp_subsec_nanos() as f64 / 1_000_000_000.0);
        timestamp.to_string()
    } else {
        // Format using the output format (DICOM standard for DA/DT, custom for others)
        let formatted = adjusted.format(output_fmt).to_string();
        if !suffix.is_empty() && vr == "DT" {
            format!("{formatted}{suffix}")
        } else {
            formatted
        }
    };
    Ok(result)
}

fn jitter(
    value: f64,
    jitter_range: f64,
    jitter_type: &str,
    jitter_min: Option<f64>,
    jitter_max: Option<f64>,
) -> Result<f64, String> {
    if jitter_range == 0.0 {
        return Err("jitter_range cannot be 0".to_string());
    }

    let mut rng = rand::rng();
    let rand_val: f64 = loop {
        let rv = if jitter_type == "int" {
            rng.random_range(-(jitter_range as i64)..=(jitter_range as i64)) as f64
        } else {
            rng.random_range(-1.0..=1.0) * jitter_range
        };
        if rv != 0.0 {
            break rv;
        }
    };

    let mut new_value = value + rand_val;

    if let Some(min) = jitter_min
        && new_value < min
    {
        new_value = min;
    }
    if let Some(max) = jitter_max
        && new_value > max
    {
        new_value = max;
    }

    Ok(new_value)
}

fn parse_da(value: &str) -> Option<NaiveDate> {
    NaiveDate::parse_from_str(value.trim(), "%Y%m%d").ok()
}

fn get_patient_age(
    birth_date: NaiveDate,
    experiment_date: NaiveDate,
    preferred_unit: Option<AgeUnit>,
) -> String {
    let days = (experiment_date - birth_date).num_days();

    if days < 1000
        && preferred_unit != Some(AgeUnit::Years)
        && preferred_unit != Some(AgeUnit::Months)
    {
        return format!("{:0>3}D", days);
    }

    // months: approximate by year*12 + month difference
    let months = (experiment_date.year() - birth_date.year()) * 12
        + (experiment_date.month() as i32 - birth_date.month() as i32);

    if months < 1000 && preferred_unit != Some(AgeUnit::Years) {
        return format!("{:0>3}M", months);
    }

    let years = experiment_date.year()
        - birth_date.year()
        - match (experiment_date.month(), experiment_date.day())
            .cmp(&(birth_date.month(), birth_date.day()))
        {
            Ordering::Less => 1,
            _ => 0,
        };

    format!("{:0>3}Y", years)
}

fn set_patient_age_from_birth_date(
    obj: &mut InMemDicomObject,
    unit: Option<AgeUnit>,
) -> Result<(), Box<dyn std::error::Error>> {
    let birth_date = obj
        .element(PATIENT_BIRTH_DATE)
        .ok()
        .and_then(|el| el.to_str().ok())
        .as_deref()
        .and_then(parse_da);
    let birth_date = match birth_date {
        Some(d) => d,
        None => return Ok(()),
    };
    let experiment_date = obj
        .element(STUDY_DATE)
        .ok()
        .and_then(|el| el.to_str().ok())
        .or_else(|| {
            obj.element(SERIES_DATE)
                .ok()
                .and_then(|el| el.to_str().ok())
        })
        .as_deref()
        .and_then(parse_da);
    let experiment_date = match experiment_date {
        Some(d) => d,
        None => return Ok(()),
    };
    let age_str = get_patient_age(birth_date, experiment_date, unit);
    obj.put_str(PATIENT_AGE, VR::AS, &age_str);
    Ok(())
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct PrivateTag {
    group: u16,
    element: u8,
    creator: String,
}

impl PrivateTag {
    fn new(group: u16, element: u8, creator: String) -> Self {
        Self {
            group,
            element,
            creator,
        }
    }
}

impl fmt::Display for PrivateTag {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "({:04X},xx{:02X}) \"{}\"",
            self.group, self.element, self.creator
        )
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum NestedItem {
    Tag(Tag),
    PrivateTag(PrivateTag),
    Index(usize),
    Wildcard,
}

fn parse_nested_field(name: &str) -> Result<Vec<NestedItem>, String> {
    let mut path = Vec::new();
    if let Some(captures) = utils::PRIVATE_TAG_RE.captures(name) {
        let group = u16::from_str_radix(captures.get(1).unwrap().as_str(), 16)
            .map_err(|e| format!("Invalid private tag group in {name}: {e}"))?;
        let creator = captures.get(2).unwrap().as_str().to_string();
        let element = u8::from_str_radix(captures.get(3).unwrap().as_str(), 16)
            .map_err(|e| format!("Invalid private tag element in {name}: {e}"))?;
        path.push(NestedItem::PrivateTag(PrivateTag::new(
            group, element, creator,
        )));
        return Ok(path);
    }

    for part in name.split('.') {
        if part == "*" {
            path.push(NestedItem::Wildcard);
        } else if part.starts_with("0x")
            || (part.len() == 8 && part.chars().all(|c| c.is_ascii_hexdigit()))
        {
            let raw = u32::from_str_radix(part.trim_start_matches("0x"), 16)
                .map_err(|e| format!("Invalid hex tag {part}: {e}"))?;
            let group = ((raw >> 16) & 0xFFFF) as u16;
            let element = (raw & 0xFFFF) as u16;
            path.push(NestedItem::Tag(Tag(group, element)));
        } else if let Ok(idx) = part.parse::<usize>() {
            path.push(NestedItem::Index(idx));
        } else {
            let tag = StandardDataDictionary
                .parse_tag(part)
                .ok_or_else(|| format!("Invalid tag name: {part}"))?;
            path.push(NestedItem::Tag(tag));
        }
    }

    Ok(path)
}

fn remove_undefined_fields(
    obj: &mut InMemDicomObject,
    allowed_paths: &[Vec<NestedItem>],
) -> Result<(), String> {
    let mut allowed_tags = std::collections::HashSet::new();
    for path in allowed_paths {
        if let Some(NestedItem::Tag(tag)) = path.first() {
            allowed_tags.insert(*tag);
        }
    }

    let tags_to_remove: Vec<Tag> = obj
        .clone()
        .into_iter()
        .map(|el| el.header().tag)
        .filter(|tag| !allowed_tags.contains(tag))
        .collect();

    for tag in tags_to_remove {
        obj.remove_element(tag);
    }

    Ok(())
}

pub fn remove_private_tags(obj: &mut InMemDicomObject, defined_private_tags: &[PrivateTag]) {
    let mut tags_to_remove = Vec::new();
    let mut updated_elements: Vec<InMemElement> = Vec::new();

    for elem in obj.iter() {
        let tag = elem.tag();

        if let dicom_core::DicomValue::Sequence(seq) = elem.value() {
            let mut new_items = Vec::new();

            for item in seq.items().iter() {
                let mut cloned = item.clone();
                remove_private_tags(&mut cloned, defined_private_tags);
                new_items.push(cloned);
            }

            updated_elements.push(DataElement::new(
                tag,
                VR::SQ,
                dicom_core::value::DataSetSequence::<InMemDicomObject>::new(
                    new_items,
                    dicom_core::Length::UNDEFINED,
                ),
            ));
        }

        if tag.0 % 2 == 1 {
            if (0x0010..=0x00FF).contains(&tag.1) {
                let creator = match elem.value().to_str() {
                    Ok(s) => s.to_string(),
                    Err(_) => String::new(),
                };
                let is_used = defined_private_tags
                    .iter()
                    .any(|pt| pt.group == tag.0 && pt.creator == creator);
                if !is_used {
                    tags_to_remove.push(tag);
                }
            } else {
                let is_defined = defined_private_tags.iter().any(|pt| {
                    if let Ok(element) = obj.private_element(pt.group, &pt.creator, pt.element) {
                        element.tag() == tag
                    } else {
                        false
                    }
                });
                if !is_defined {
                    tags_to_remove.push(tag);
                }
            }
        }
    }

    for updated in updated_elements {
        obj.put(updated);
    }
    for tag in tags_to_remove {
        obj.remove_element(tag);
    }
}

fn substitute_template(
    template: &str,
    regex_captures: &HashMap<String, String>,
    dicom_obj: &InMemDicomObject,
) -> Result<String, String> {
    let var_re = Regex::new(r"\{([^}]+)\}").unwrap();
    let mut result = template.to_string();
    let mut errors = Vec::new();

    for cap in var_re.captures_iter(template) {
        let full_match = cap.get(0).unwrap().as_str();
        let var_name = cap.get(1).unwrap().as_str();

        // first check if it's a regex capture
        if let Some(value) = regex_captures.get(var_name) {
            result = result.replace(full_match, value);
            continue;
        }

        // then try to resolve as DICOM tag
        match resolve_dicom_tag_value(dicom_obj, var_name) {
            Ok(value) => {
                result = result.replace(full_match, &value);
            }
            Err(e) => {
                errors.push(format!("Variable '{}': {}", var_name, e));
            }
        }
    }

    if !errors.is_empty() {
        return Err(format!(
            "Template substitution failed: {}",
            errors.join("; ")
        ));
    }

    Ok(result)
}

/// Resolve a DICOM tag identifier to its string value
/// Supports:
/// - Tag names: "SOPInstanceUID", "PatientID"
/// - Hex format: "00080018", "0x00080018"
/// - Tuple format: "(0008, 0018)"
/// - Private tags: "(0009, \"GEMS_IMAG_01\", 01)"
fn resolve_dicom_tag_value(obj: &InMemDicomObject, tag_name: &str) -> Result<String, String> {
    let tag_identifier = if let Some(captures) = DICOM_TAG_TUPLE_RE.captures(tag_name) {
        // tuple format: (0010, 0010)
        format!(
            "{}{}",
            captures.get(1).unwrap().as_str(),
            captures.get(2).unwrap().as_str()
        )
    } else {
        tag_name.to_string()
    };
    // parse as nested field to get the tag
    let parsed_path = parse_nested_field(&tag_identifier)?;
    if parsed_path.len() != 1 {
        return Err(format!(
            "Tag identifier must be a single tag, not a nested path: {tag_name}"
        ));
    }
    match &parsed_path[0] {
        NestedItem::Tag(tag) => {
            let value = get_dcm_value(obj, *tag)
                .map_err(|e| format!("Failed to read tag {tag_name}: {e}"))?;

            if matches!(value, DicomValue::Empty) {
                return Err(format!("Tag {tag_name} has no value"));
            }

            Ok(value.to_string())
        }
        NestedItem::PrivateTag(private_tag) => {
            match obj.private_element(private_tag.group, &private_tag.creator, private_tag.element)
            {
                Ok(elem) => {
                    match elem.to_str() {
                        Ok(s) => Ok(s.to_string()),
                        Err(_) => {
                            // try to get raw value if string conversion fails
                            match elem.value() {
                                dicom_core::value::Value::Primitive(p) => {
                                    Ok(p.to_str().to_string())
                                }
                                _ => Err(format!("Failed to read private tag {tag_name}")),
                            }
                        }
                    }
                }
                Err(_) => Err(format!("Private tag {tag_name} not found or has no value")),
            }
        }
        _ => Err(format!("Invalid tag identifier: {tag_name}")),
    }
}

fn empty_array_to_string<'de, D>(deserializer: D) -> Result<Option<String>, D::Error>
where
    D: Deserializer<'de>,
{
    #[derive(Deserialize)]
    #[serde(untagged)]
    #[allow(dead_code)]
    enum StringOrArray {
        Str(String),
        Int(i64),
        Float(f64),
        Array(Vec<serde_yaml::Value>),
    }

    match StringOrArray::deserialize(deserializer)? {
        StringOrArray::Str(s) => Ok(Some(s)),
        StringOrArray::Int(i) => Ok(Some(i.to_string())),
        StringOrArray::Float(f) => Ok(Some(f.to_string())),
        StringOrArray::Array(_) => Ok(Some("".to_string())),
    }
}

fn deserialize_file_filter<'de, D>(deserializer: D) -> Result<Option<Vec<String>>, D::Error>
where
    D: Deserializer<'de>,
{
    #[derive(Deserialize)]
    #[serde(untagged)]
    enum StringOrVec {
        Str(String),
        Vec(Vec<String>),
    }

    match Option::<StringOrVec>::deserialize(deserializer)? {
        None => Ok(None),
        Some(StringOrVec::Str(s)) => Ok(Some(vec![s])),
        Some(StringOrVec::Vec(v)) => Ok(Some(v)),
    }
}
