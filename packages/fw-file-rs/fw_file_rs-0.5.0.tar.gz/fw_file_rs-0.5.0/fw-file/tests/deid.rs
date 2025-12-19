use std::collections::HashMap;

use dicom_core::{Tag, VR};
use fw_file::dcm::{CreateDicomValue, DeidProfile, ProfileParseError, create_dcm_as_bytes};
use rstest::rstest;

#[rstest]
#[case("StudyDate")]
#[case("00080020")]
#[case("(0008, 0020)")]
#[case("0x00080020")]
fn test_deid_replace_study_date_by_various_tag_formats(#[case] tag_identifier: &str) {
    let tags = HashMap::from([
        ("PatientName", "Test^Patient".into()),
        ("StudyDate", "20000101".into()),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let yaml = format!(
        r#"
version: 1
name: test profile
dicom:
  fields:
    - name: "{tag_identifier}"
      replace-with: "20220101"
"#
    );

    let profile = DeidProfile::from_yaml(&yaml).unwrap();
    let result = profile.deid_dcm(&dcm).expect("deid failed");

    let obj = dicom_object::from_reader(result.as_slice()).unwrap();
    let val = obj.element_by_name("StudyDate").unwrap().to_str().unwrap();
    assert_eq!(val, "20220101");
}

#[test]
fn test_deid_remove_field() {
    let tags = HashMap::from([
        ("PatientName", "Test^Patient".into()),
        ("PatientID", "123456".into()),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let yaml = r#"
version: 1
name: test profile
dicom:
  fields:
    - name: PatientID
      remove: true
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).expect("deid failed");

    let obj = dicom_object::from_reader(result.as_slice()).unwrap();
    assert!(obj.element_by_name("PatientID").is_err());
    let val = obj
        .element_by_name("PatientName")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "Test^Patient");
}

#[test]
fn test_validate_vr_date_invalid() {
    let tags = HashMap::from([("StudyDate", "20000101".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let yaml = r#"
version: 1
name: test profile
dicom:
  fields:
    - name: StudyDate
      replace-with: "notadate"
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let err = profile.deid_dcm(&dcm).unwrap_err();
    assert!(err.contains("cannot be parsed as DA"));
}

#[test]
fn test_deid_replace_patient_name() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  fields:
    - name: PatientName
      replace-with: "Anon^Patient"
"#;

    let tags = HashMap::from([("PatientName", "Test^Patient".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("PatientName")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "Anon^Patient");
}

#[test]
fn test_deid_hash_patient_name() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  fields:
    - name: PatientName
      hash: true
"#;

    let tags = HashMap::from([("PatientName", "Test^Patient".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("PatientName")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "7a33e38537816612");
}

#[test]
fn test_deid_hash_patient_name_with_salt() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  salt: "my-secret-salt"
  fields:
    - name: PatientName
      hash: true
"#;

    let tags = HashMap::from([("PatientName", "Test^Patient".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("PatientName")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "79003a5ab0b0e322");
}

#[test]
fn test_deid_hash_study_instance_uid() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  fields:
    - name: StudyInstanceUID
      hashuid: true
"#;

    let tags = HashMap::from([(
        "StudyInstanceUID",
        "1.2.840.113619.6.283.4.983142589.7316.1300473420.841".into(),
    )]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("StudyInstanceUID")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(
        val,
        "1.2.840.113619.551726.420312.177022.222461.230571.501817.841"
    );
}

#[test]
fn test_deid_hash_study_instance_uid_with_salt() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  salt: "my-secret-salt"
  fields:
    - name: StudyInstanceUID
      hashuid: true
"#;

    let tags = HashMap::from([(
        "StudyInstanceUID",
        "1.2.840.113619.6.283.4.983142589.7316.1300473420.841".into(),
    )]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("StudyInstanceUID")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(
        val,
        "1.2.840.113619.203194.181166.142180.115115.819315.501102.841"
    );
}

#[test]
fn test_deid_increment_patient_birth_date() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: 11
  fields:
    - name: PatientBirthDate
      increment-date: true
"#;

    let tags = HashMap::from([("PatientBirthDate", "19990101".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("PatientBirthDate")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "19990112");
}

#[test]
fn test_deid_increment_date_empty_value() {
    let yaml = format!(
        r#"
version: 1
name: test profile
dicom:
  jitter-range: 10
  jitter-type: int
  date-increment: 11
  fields:
    - name: PatientBirthDate
      increment-date: true
    - name: PatientWeight
      jitter: true
    - name: StudyInstanceUID
      hashuid: true
    - name: PatientID
      hash: true
"#
    );

    let tags = HashMap::from([
        ("PatientBirthDate", "".into()),
        ("PatientWeight", "".into()),
        ("StudyInstanceUID", "".into()),
        ("PatientID", "".into()),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(&yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    for field in [
        "PatientBirthDate",
        "PatientWeight",
        "StudyInstanceUID",
        "PatientID",
    ] {
        let val = obj.element_by_name(field).unwrap().to_str().unwrap();
        assert_eq!(val, "");
    }
}

#[test]
fn test_deid_jitter_patient_weight() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  jitter-range: 10
  jitter-type: int
  fields:
    - name: PatientWeight
      jitter: true
"#;

    let tags = HashMap::from([("PatientWeight", 55.into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("PatientWeight")
        .unwrap()
        .to_str()
        .unwrap()
        .trim()
        .parse::<i64>()
        .unwrap();
    assert_ne!(val, 55);
}

#[test]
fn test_deid_patient_age_from_birthdate() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  patient-age-from-birthdate: true
  patient-age-units: Y
  fields:
    - name: PatientBirthDate
      remove: true
"#;

    let tags = HashMap::from([
        ("PatientBirthDate", "20000101".into()),
        ("StudyDate", "20220101".into()),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    assert!(obj.element_by_name("PatientBirthDate").is_err());
    let val = obj.element_by_name("PatientAge").unwrap().to_str().unwrap();
    assert_eq!(val, "022Y");
}

#[test]
fn test_deid_recurse_sequence() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  recurse-sequence: true
  fields:
    - name: StudyInstanceUID
      hashuid: true
"#;

    let seq_item = HashMap::from([
        (
            "StudyInstanceUID",
            "1.2.840.113619.6.283.4.983142589.7316.1300473420.841".into(),
        ),
        ("StudyDate", "20220101".into()),
    ]);
    let tags = HashMap::from([("ReferencedStudySequence", vec![seq_item].into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let study_uid = if let dicom_core::DicomValue::Sequence(seq) = obj
        .element_by_name("ReferencedStudySequence")
        .unwrap()
        .value()
    {
        seq.items()
            .get(0)
            .and_then(|item| item.element_by_name("StudyInstanceUID").ok())
            .and_then(|e| e.to_str().ok())
            .unwrap()
    } else {
        panic!("ReferencedStudySequence is not a sequence!");
    };
    assert_eq!(
        study_uid,
        "1.2.840.113619.551726.420312.177022.222461.230571.501817.841"
    );
}

#[test]
fn test_deid_replace_with_sequence() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  recurse-sequence: true
  fields:
    - name: ReferencedStudySequence
      replace-with: []
"#;

    let seq_item = HashMap::from([(
        "StudyInstanceUID",
        "1.2.840.113619.6.283.4.983142589.7316.1300473420.841".into(),
    )]);
    let tags = HashMap::from([("ReferencedStudySequence", vec![seq_item].into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let sequence = obj.element_by_name("ReferencedStudySequence").unwrap();
    match sequence.value() {
        dicom_core::DicomValue::Sequence(seq) => {
            assert!(seq.items().is_empty(), "Sequence is not empty!");
        }
        _ => panic!("ReferencedStudySequence is not a sequence!"),
    }
}

#[test]
fn test_deid_remove_undefined() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  remove-undefined: true
  fields:
    - name: ReferencedStudySequence.*.StudyInstanceUID
    - name: PatientAge
      replace-with: REDACTED
"#;

    let seq_item = HashMap::from([
        (
            "StudyInstanceUID",
            "1.2.840.113619.6.283.4.983142589.7316.1300473420.841".into(),
        ),
        ("StudyDate", "20220101".into()),
    ]);
    let tags = HashMap::from([
        ("PatientAge", "022Y".into()),
        ("ReferencedStudySequence", vec![seq_item].into()),
        (
            "StudyInstanceUID",
            "1.2.840.113619.6.283.4.983142589.7316.1300473420.841".into(),
        ),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    assert!(obj.element_by_name("StudyInstanceUID").is_err());
    let study_uid = if let dicom_core::DicomValue::Sequence(seq) = obj
        .element_by_name("ReferencedStudySequence")
        .unwrap()
        .value()
    {
        seq.items()
            .get(0)
            .and_then(|item| item.element_by_name("StudyInstanceUID").ok())
            .and_then(|e| e.to_str().ok())
            .unwrap()
    } else {
        panic!("ReferencedStudySequence is not a sequence!");
    };
    assert_eq!(
        study_uid,
        "1.2.840.113619.6.283.4.983142589.7316.1300473420.841"
    );
    let val = obj.element_by_name("PatientAge").unwrap().to_str().unwrap();
    assert_eq!(val, "REDACTED");
}

#[test]
fn test_deid_regex_field() {
    let tags = HashMap::from([
        ("StudyDate", "20250908".into()),
        ("SeriesDate", "20250908".into()),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: 10
  fields:
    - regex: .*Date.*
      increment-date: true
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).expect("deid failed");

    let obj = dicom_object::from_reader(result.as_slice()).unwrap();
    let val = obj.element_by_name("StudyDate").unwrap().to_str().unwrap();
    assert_eq!(val, "20250918");
    let val = obj.element_by_name("SeriesDate").unwrap().to_str().unwrap();
    assert_eq!(val, "20250918");
}

#[test]
fn test_deid_regex_field_hex() {
    let tags = HashMap::from([
        ("StudyDate", "20250908".into()),
        ("SeriesDate", "20250908".into()),
        ("PatientBirthDate", "20000101".into()),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: 10
  fields:
    - regex: 0008002.*
      increment-date: true
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).expect("deid failed");

    let obj = dicom_object::from_reader(result.as_slice()).unwrap();
    let val = obj.element_by_name("StudyDate").unwrap().to_str().unwrap();
    assert_eq!(val, "20250918");
    let val = obj.element_by_name("SeriesDate").unwrap().to_str().unwrap();
    assert_eq!(val, "20250918");
    let val = obj
        .element_by_name("PatientBirthDate")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "20000101");
}

#[test]
fn test_deid_private_tag() {
    let tags = HashMap::from([
        ("0009,0010", "GEMS_IMAG_01".into()),
        (
            "0009,1001",
            CreateDicomValue::PrimitiveAndVR("some value".into(), VR::LO),
        ),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let yaml = r#"
version: 1
name: test profile
dicom:
  fields:
    - name: (0009, "GEMS_IMAG_01", 01)
      replace-with: "REDACTED"
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).expect("deid failed");

    let obj = dicom_object::from_reader(result.as_slice()).unwrap();
    let val = obj.element(Tag(0x0009, 0x1001)).unwrap().to_str().unwrap();
    assert_eq!(val, "REDACTED");
}

#[test]
fn test_deid_replace_with_upsert_private_tag() {
    let tags = HashMap::from([("StudyDate", "20250908".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let yaml = r#"
version: 1
name: test profile
dicom:
  fields:
    - name: (0031, "AGFA PACS Archive Mirroring 1.0", 01)
      replace-with: "1758127490"
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).expect("deid failed");

    let obj = dicom_object::from_reader(result.as_slice()).unwrap();
    let val = obj.element(Tag(0x0031, 0x0001)).unwrap().to_str().unwrap();
    assert_eq!(val, "AGFA PACS Archive Mirroring 1.0");
    let val = obj.element(Tag(0x0031, 0x0101)).unwrap().to_str().unwrap();
    assert_eq!(val, "1758127490");
}

#[test]
fn test_deid_remove_private_tags() {
    let tags = HashMap::from([
        ("StudyDate", "20250908".into()),
        ("2005,0010", "Philips MR Imaging DD 001".into()),
        (
            "2005,1070",
            CreateDicomValue::PrimitiveAndVR("some value".into(), VR::LO),
        ),
        (
            "2005,1071",
            CreateDicomValue::PrimitiveAndVR(2.1.into(), VR::FL),
        ),
        ("2005,0020", "Philips MR Imaging DD 002".into()),
        (
            "2005,202d",
            CreateDicomValue::PrimitiveAndVR("value".into(), VR::FL),
        ),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let yaml = r#"
version: 1
name: test profile
dicom:
  remove-private-tags: true
  fields:
    - name: (2005, "Philips MR Imaging DD 001", 70)
      replace-with: "REDACTED"
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).expect("deid failed");

    let obj = dicom_object::from_reader(result.as_slice()).unwrap();
    // remove private tags
    assert!(obj.element(Tag(0x2005, 0x0020)).is_err());
    assert!(obj.element(Tag(0x2005, 0x202d)).is_err());
    assert!(obj.element(Tag(0x2005, 0x1071)).is_err());
    // other tags are kept
    let val = obj.element_by_name("StudyDate").unwrap().to_str().unwrap();
    assert_eq!(val, "20250908");
    let val = obj.element(Tag(0x2005, 0x0010)).unwrap().to_str().unwrap();
    assert_eq!(val, "Philips MR Imaging DD 001");
    let val = obj.element(Tag(0x2005, 0x1070)).unwrap().to_str().unwrap();
    assert_eq!(val, "REDACTED");
}

#[test]
fn test_profile_deid_repeater_tag() {
    let tags = HashMap::from([
        ("6000,0022", "some value".into()),
        ("6002,0022", "some value".into()),
        ("6004,0022", "some value".into()),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let yaml = r#"
version: 1
name: test profile
dicom:
  remove-private-tags: true
  fields:
    - name: (60xx, 0022)
      replace-with: REDACTED
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).expect("deid failed");
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();
    let val = obj.element(Tag(0x6000, 0x0022)).unwrap().to_str().unwrap();
    assert_eq!(val, "REDACTED");
    let val = obj.element(Tag(0x6002, 0x0022)).unwrap().to_str().unwrap();
    assert_eq!(val, "REDACTED");
    let val = obj.element(Tag(0x6004, 0x0022)).unwrap().to_str().unwrap();
    assert_eq!(val, "REDACTED");
}

#[test]
fn test_profile_unsupported_version() {
    let yaml = r#"
version: 99
name: test
dicom: {}
"#;

    let err = DeidProfile::from_yaml(yaml).unwrap_err();
    match err {
        ProfileParseError::UnsupportedVersion(v) => assert_eq!(v, 99),
        e => panic!("Expected UnsupportedVersion, got {e:?}"),
    }
}

#[test]
fn test_deid_hash_uid_with_custom_prefix_fields() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  uid-prefix-fields: 2
  fields:
    - name: StudyInstanceUID
      hashuid: true
"#;

    let tags = HashMap::from([(
        "StudyInstanceUID",
        "1.2.840.113619.6.283.4.983142589.7316.1300473420.841".into(),
    )]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("StudyInstanceUID")
        .unwrap()
        .to_str()
        .unwrap();
    assert!(val.starts_with("1.2."));
    assert_ne!(
        val,
        "1.2.840.113619.551726.420312.177022.222461.230571.501817.841"
    );
}

#[test]
fn test_deid_hash_uid_with_custom_suffix_fields() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  uid-suffix-fields: 2
  fields:
    - name: StudyInstanceUID
      hashuid: true
"#;

    let tags = HashMap::from([(
        "StudyInstanceUID",
        "1.2.840.113619.6.283.4.983142589.7316.1300473420.841".into(),
    )]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("StudyInstanceUID")
        .unwrap()
        .to_str()
        .unwrap();
    assert!(val.ends_with(".473.841"));
}

#[test]
fn test_deid_hash_uid_with_numeric_name() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  uid-prefix-fields: 4
  uid-numeric-name: "9.9.9.9"
  fields:
    - name: StudyInstanceUID
      hashuid: true
"#;

    let tags = HashMap::from([(
        "StudyInstanceUID",
        "1.2.840.113619.6.283.4.983142589.7316.1300473420.841".into(),
    )]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("StudyInstanceUID")
        .unwrap()
        .to_str()
        .unwrap();
    assert!(val.starts_with("9.9.9.9."));
    assert_ne!(
        val,
        "1.2.840.113619.551726.420312.177022.222461.230571.501817.841"
    );
}

#[test]
fn test_deid_hash_uid_with_all_custom_options() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  uid-prefix-fields: 3
  uid-suffix-fields: 2
  uid-numeric-name: "8.8.8"
  fields:
    - name: StudyInstanceUID
      hashuid: true
"#;

    let tags = HashMap::from([(
        "StudyInstanceUID",
        "1.2.840.113619.6.283.4.983142589.7316.1300473420.841".into(),
    )]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("StudyInstanceUID")
        .unwrap()
        .to_str()
        .unwrap();
    assert!(val.starts_with("8.8.8."));
    assert!(val.ends_with(".473420.841"));
}

#[test]
fn test_deid_hash_uid_zero_prefix_handling() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  fields:
    - name: StudyInstanceUID
      hashuid: true
"#;

    let tags = HashMap::from([("StudyInstanceUID", "1.2.3.4.5.6.7.8.9.10.11".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("StudyInstanceUID")
        .unwrap()
        .to_str()
        .unwrap();

    let parts: Vec<&str> = val.split('.').collect();
    for (i, part) in parts.iter().enumerate() {
        if i >= 4 && i < 10 {
            assert!(
                !part.starts_with('0'),
                "Hash segment should not start with 0: {}",
                part
            );
        }
    }
}

#[test]
fn test_deid_replace_with_insert_false_global() {
    // Test that with replace-with-insert: false globally,
    // fields that don't exist are NOT inserted
    let yaml = r#"
version: 1
name: test profile
dicom:
  replace-with-insert: false
  fields:
    - name: PatientName
      replace-with: "Anon^Patient"
    - name: PatientComments
      replace-with: "Should not be inserted"
"#;

    let tags = HashMap::from([("PatientName", "Test^Patient".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    // PatientName exists, so it should be replaced
    let val = obj
        .element_by_name("PatientName")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "Anon^Patient");

    // PatientComments does not exist, so it should NOT be inserted
    assert!(obj.element_by_name("PatientComments").is_err());
}

#[test]
fn test_deid_replace_with_insert_true_global() {
    // Test that with replace-with-insert: true globally (or default),
    // fields that don't exist ARE inserted
    let yaml = r#"
version: 1
name: test profile
dicom:
  replace-with-insert: true
  fields:
    - name: PatientName
      replace-with: "Anon^Patient"
    - name: PatientComments
      replace-with: "Inserted comment"
"#;

    let tags = HashMap::from([("PatientName", "Test^Patient".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    // PatientName exists, so it should be replaced
    let val = obj
        .element_by_name("PatientName")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "Anon^Patient");

    // PatientComments does not exist, but should be inserted
    let val = obj
        .element_by_name("PatientComments")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "Inserted comment");
}

#[test]
fn test_deid_replace_with_insert_default_behavior() {
    // Test that without specifying replace-with-insert, the default is true (insert)
    let yaml = r#"
version: 1
name: test profile
dicom:
  fields:
    - name: PatientName
      replace-with: "Anon^Patient"
    - name: PatientComments
      replace-with: "Inserted by default"
"#;

    let tags = HashMap::from([("PatientName", "Test^Patient".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    // PatientName exists, so it should be replaced
    let val = obj
        .element_by_name("PatientName")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "Anon^Patient");

    // PatientComments does not exist, but should be inserted (default behavior)
    let val = obj
        .element_by_name("PatientComments")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "Inserted by default");
}

#[test]
fn test_deid_replace_with_insert_field_override() {
    // Test that field-level replace-with-insert overrides global setting
    let yaml = r#"
version: 1
name: test profile
dicom:
  replace-with-insert: false
  fields:
    - name: PatientName
      replace-with: "Anon^Patient"
    - name: PatientComments
      replace-with: "Should be inserted due to field override"
      replace-with-insert: true
    - name: StudyDescription
      replace-with: "Should not be inserted"
"#;

    let tags = HashMap::from([("PatientName", "Test^Patient".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    // PatientName exists, so it should be replaced
    let val = obj
        .element_by_name("PatientName")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "Anon^Patient");

    // PatientComments has field-level override to insert
    let val = obj
        .element_by_name("PatientComments")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "Should be inserted due to field override");

    // StudyDescription follows global setting (no insert)
    assert!(obj.element_by_name("StudyDescription").is_err());
}

#[test]
fn test_deid_replace_with_insert_false_field_override() {
    // Test that field-level replace-with-insert: false prevents insertion
    // even when global is true
    let yaml = r#"
version: 1
name: test profile
dicom:
  replace-with-insert: true
  fields:
    - name: PatientName
      replace-with: "Anon^Patient"
    - name: PatientComments
      replace-with: "Should not be inserted due to field override"
      replace-with-insert: false
    - name: StudyDescription
      replace-with: "Should be inserted"
"#;

    let tags = HashMap::from([("PatientName", "Test^Patient".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    // PatientName exists, so it should be replaced
    let val = obj
        .element_by_name("PatientName")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "Anon^Patient");

    // PatientComments has field-level override to NOT insert
    assert!(obj.element_by_name("PatientComments").is_err());

    // StudyDescription follows global setting (insert)
    let val = obj
        .element_by_name("StudyDescription")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "Should be inserted");
}

#[test]
fn test_deid_replace_with_insert_false_private_tag() {
    // Test that replace-with-insert: false works with private tags
    let tags = HashMap::from([
        ("StudyDate", "20250908".into()),
        ("0009,0010", "GEMS_IMAG_01".into()),
        (
            "0009,1001",
            CreateDicomValue::PrimitiveAndVR("existing value".into(), VR::LO),
        ),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let yaml = r#"
version: 1
name: test profile
dicom:
  replace-with-insert: false
  fields:
    - name: (0009, "GEMS_IMAG_01", 01)
      replace-with: "REPLACED"
    - name: (0009, "GEMS_IMAG_01", 02)
      replace-with: "SHOULD NOT INSERT"
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).expect("deid failed");

    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    // Existing private tag should be replaced
    let val = obj.element(Tag(0x0009, 0x1001)).unwrap().to_str().unwrap();
    assert_eq!(val, "REPLACED");

    // Non-existing private tag should NOT be inserted
    assert!(obj.element(Tag(0x0009, 0x1002)).is_err());
}

#[test]
fn test_deid_replace_with_insert_true_private_tag() {
    // Test that replace-with-insert: true works with private tags (inserts new)
    let tags = HashMap::from([("StudyDate", "20250908".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let yaml = r#"
version: 1
name: test profile
dicom:
  replace-with-insert: true
  fields:
    - name: (0031, "AGFA PACS Archive Mirroring 1.0", 01)
      replace-with: "1758127490"
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).expect("deid failed");

    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    // Private tag creator should be inserted
    let val = obj.element(Tag(0x0031, 0x0001)).unwrap().to_str().unwrap();
    assert_eq!(val, "AGFA PACS Archive Mirroring 1.0");

    // Private tag should be inserted
    let val = obj.element(Tag(0x0031, 0x0101)).unwrap().to_str().unwrap();
    assert_eq!(val, "1758127490");
}

#[test]
fn test_deid_increment_date_with_override() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: 10
  fields:
    - name: PatientBirthDate
      increment-date: true
    - name: StudyDate
      increment-date: true
      date-increment-override: 30
"#;

    let tags = HashMap::from([
        ("PatientBirthDate", "20000101".into()),
        ("StudyDate", "20000101".into()),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    // PatientBirthDate should use global increment of 10 days
    let val = obj
        .element_by_name("PatientBirthDate")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "20000111");

    // StudyDate should use field-level override of 30 days
    let val = obj.element_by_name("StudyDate").unwrap().to_str().unwrap();
    assert_eq!(val, "20000131");
}

#[test]
fn test_deid_increment_date_with_custom_format() {
    // Custom format is used for PARSING, but output uses DICOM standard format
    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: 5
  fields:
    - name: PatientBirthDate
      increment-date: true
      date-format: "%Y-%m-%d"
"#;

    let tags = HashMap::from([("PatientBirthDate", "2000-01-01".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("PatientBirthDate")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "20000106");
}

#[test]
fn test_deid_increment_date_with_custom_format_on_text_field() {
    // Custom format is used for BOTH parsing AND output
    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: 5
  fields:
    - name: StudyDescription
      increment-date: true
      date-format: "%Y-%m-%d"
"#;

    let tags = HashMap::from([("StudyDescription", "2000-01-01".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("StudyDescription")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "2000-01-06");
}

#[test]
fn test_deid_increment_datetime_default_format() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: 1
  fields:
    - name: AcquisitionDateTime
      increment-datetime: true
"#;

    let tags = HashMap::from([
        ("StudyDate", "20000101".into()),
        ("AcquisitionDateTime", "20000101120000.000000".into()),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("AcquisitionDateTime")
        .unwrap()
        .to_str()
        .unwrap();
    // Should preserve fractional seconds in output and increment by 1 day
    assert!(val.contains('.'));
    assert!(val.starts_with("20000102")); // Date should be incremented
}

#[test]
fn test_deid_increment_datetime_with_custom_format() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: 5
  fields:
    - name: StudyDescription
      increment-datetime: true
      datetime-format: "%Y-%m-%d %H:%M:%S"
"#;

    let tags = HashMap::from([("StudyDescription", "2000-01-01 12:30:00".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("StudyDescription")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "2000-01-06 12:30:00");
}

#[test]
fn test_deid_increment_datetime_on_dt_field() {
    // Output should use DICOM standard DT format
    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: 2
  fields:
    - name: AcquisitionDateTime
      increment-datetime: true
      datetime-format: "%Y-%m-%d %H:%M:%S"
"#;

    let tags = HashMap::from([("AcquisitionDateTime", "2000-01-01 14:30:00".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("AcquisitionDateTime")
        .unwrap()
        .to_str()
        .unwrap();
    assert!(val.starts_with("20000103143000"));
    assert!(val.contains('.')); // Should have fractional seconds
}

#[test]
fn test_deid_increment_date_with_datetime_min() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: -100
  datetime-min: "20000101"
  fields:
    - name: PatientBirthDate
      increment-date: true
"#;

    let tags = HashMap::from([("PatientBirthDate", "20000201".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("PatientBirthDate")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "20000101");
}

#[test]
fn test_deid_increment_date_with_datetime_max() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: 100
  datetime-max: "20000131"
  fields:
    - name: PatientBirthDate
      increment-date: true
"#;

    let tags = HashMap::from([("PatientBirthDate", "20000101".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("PatientBirthDate")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "20000131");
}

#[test]
fn test_deid_increment_date_with_relative_datetime_min() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: 1
  datetime-min: "-1years"
  fields:
    - name: PatientBirthDate
      increment-date: true
"#;
    // Use a date far in the past that would violate the constraint
    let tags = HashMap::from([("PatientBirthDate", "19500101".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("PatientBirthDate")
        .unwrap()
        .to_str()
        .unwrap();
    assert_ne!(val, "19500102");
}

#[test]
fn test_deid_increment_date_multivalue() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: 10
  fields:
    - name: StudyDate
      increment-date: true
"#;

    let tags = HashMap::from([("StudyDate", "20000101,20000201,20000301".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj.element_by_name("StudyDate").unwrap().to_str().unwrap();
    // Each value should be incremented by 10 days
    assert_eq!(val, "20000111\\20000211\\20000311");
}

#[test]
fn test_deid_increment_date_field_level_datetime_min_max() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: 200
  datetime-min: "19000101"
  datetime-max: "21000101"
  fields:
    - name: PatientBirthDate
      increment-date: true
      datetime-min: "20000101"
      datetime-max: "20000630"
"#;

    let tags = HashMap::from([("PatientBirthDate", "20000301".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("PatientBirthDate")
        .unwrap()
        .to_str()
        .unwrap();
    assert_eq!(val, "20000630");
}

#[test]
fn test_deid_increment_date_with_jitter() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: 0
  jitter-date: true
  jitter-range: 5
  jitter-unit: "days"
  fields:
    - name: PatientBirthDate
      increment-date: true
"#;

    let tags = HashMap::from([("PatientBirthDate", "20000101".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("PatientBirthDate")
        .unwrap()
        .to_str()
        .unwrap();
    assert_ne!(val, "20000101");
}

#[test]
fn test_deid_increment_date_jitter_with_weeks_unit() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: 0
  jitter-date: true
  jitter-range: 2
  jitter-unit: "weeks"
  fields:
    - name: StudyDate
      increment-date: true
"#;

    let tags = HashMap::from([("StudyDate", "20000101".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj.element_by_name("StudyDate").unwrap().to_str().unwrap();
    assert_ne!(val, "20000101");
}

#[test]
fn test_deid_increment_date_field_level_jitter_override() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: 10
  fields:
    - name: PatientBirthDate
      increment-date: true
      jitter-date: true
      jitter-range: 3
      jitter-unit: "days"
"#;

    let tags = HashMap::from([("PatientBirthDate", "20000101".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj
        .element_by_name("PatientBirthDate")
        .unwrap()
        .to_str()
        .unwrap();
    assert_ne!(val, "20000101");
}

#[test]
fn test_deid_increment_date_combined_features() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  date-increment: 30
  jitter-date: true
  jitter-range: 5
  jitter-unit: "days"
  datetime-min: "20000201"
  datetime-max: "20000331"
  fields:
    - name: StudyDate
      increment-date: true
"#;

    let tags = HashMap::from([("StudyDate", "20000101".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let result = profile.deid_dcm(&dcm).unwrap();
    let obj = dicom_object::from_reader(result.as_slice()).unwrap();

    let val = obj.element_by_name("StudyDate").unwrap().to_str().unwrap();
    // Parse the result to verify it's within bounds
    // Base would be 20000131 + jitter (±5 days) = between 20000126 and 20000205
    // Then clamped to min 20000201, so should be between 20000201 and 20000205
    let year: i32 = val[0..4].parse().unwrap();
    let month: i32 = val[4..6].parse().unwrap();
    let day: i32 = val[6..8].parse().unwrap();

    assert_eq!(year, 2000);
    assert_eq!(month, 2);
    assert!(day >= 1); // Should be at least the minimum
}

#[test]
fn test_file_filter_single_pattern() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  file-filter: "*.dcm"
  fields:
    - name: PatientName
      replace-with: "Anon^Patient"
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    // test matching files
    assert!(profile.matches_file_filter("test.dcm"));
    assert!(profile.matches_file_filter("/path/to/file.dcm"));
    // test non-matching files (glob patterns are case-sensitive)
    assert!(!profile.matches_file_filter("image.DCM"));
    assert!(!profile.matches_file_filter("test.tiff"));
    assert!(!profile.matches_file_filter("file.png"));
}

#[test]
fn test_file_filter_multiple_patterns() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  file-filter: ["*.dcm", "*.tiff", "*.tif"]
  fields:
    - name: PatientName
      replace-with: "Anon^Patient"
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    // test matching files for different patterns
    assert!(profile.matches_file_filter("test.dcm"));
    assert!(profile.matches_file_filter("image.tiff"));
    assert!(profile.matches_file_filter("scan.tif"));
    assert!(profile.matches_file_filter("/var/data/file.dcm"));
    // test non-matching files
    assert!(!profile.matches_file_filter("test.png"));
    assert!(!profile.matches_file_filter("file.jpg"));
}

#[test]
fn test_file_filter_none() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  fields:
    - name: PatientName
      replace-with: "Anon^Patient"
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    // when no filter is specified, all files should match
    assert!(profile.matches_file_filter("test.dcm"));
    assert!(profile.matches_file_filter("test.tiff"));
    assert!(profile.matches_file_filter("test.png"));
    assert!(profile.matches_file_filter("anything.xyz"));
}

#[test]
fn test_file_filter_question_mark_wildcard() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  file-filter: "image?.dcm"
  fields:
    - name: PatientName
      replace-with: "Anon^Patient"
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    // test single character wildcard
    assert!(profile.matches_file_filter("image1.dcm"));
    assert!(profile.matches_file_filter("imageA.dcm"));
    // should not match multiple characters or no character
    assert!(!profile.matches_file_filter("image.dcm"));
    assert!(!profile.matches_file_filter("image12.dcm"));
}

#[test]
fn test_file_filter_character_class() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  file-filter: "file[123].dcm"
  fields:
    - name: PatientName
      replace-with: "Anon^Patient"
"#;
    let profile = DeidProfile::from_yaml(yaml).unwrap();
    // test character class matching
    assert!(profile.matches_file_filter("file1.dcm"));
    assert!(profile.matches_file_filter("file2.dcm"));
    assert!(profile.matches_file_filter("file3.dcm"));
    // should not match characters outside the class
    assert!(!profile.matches_file_filter("file4.dcm"));
    assert!(!profile.matches_file_filter("fileA.dcm"));
}

#[test]
fn test_file_filter_negated_character_class() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  file-filter: "file[!0-9].dcm"
  fields:
    - name: PatientName
      replace-with: "Anon^Patient"
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    // test negated character class - should match non-digits
    assert!(profile.matches_file_filter("fileA.dcm"));
    assert!(profile.matches_file_filter("fileB.dcm"));
    // should not match digits
    assert!(!profile.matches_file_filter("file1.dcm"));
    assert!(!profile.matches_file_filter("file5.dcm"));
}

#[test]
fn test_file_filter_path_handling() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  file-filter: "*.dcm"
  fields:
    - name: PatientName
      replace-with: "Anon^Patient"
"#;

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    // pattern should match against filename only, not full path
    assert!(profile.matches_file_filter("/home/user/data/test.dcm"));
    assert!(profile.matches_file_filter("relative/path/test.dcm"));
    assert!(profile.matches_file_filter("test.dcm"));
    // even if path has .dcm in a directory name, filename matters
    assert!(!profile.matches_file_filter("/home.dcm/user/test.tiff"));
}

#[test]
fn test_filename_rename_basic() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  filenames:
    - input-regex: '^(?P<prefix>\w+)-(?P<date>\d{4}-\d{2}-\d{2})\.dcm$'
      output: '{SOPInstanceUID}_{date}.dcm'
"#;

    let tags = HashMap::from([
        ("SOPInstanceUID", "1.2.3.4.5.6.7.8.9".into()),
        ("StudyDate", "20220101".into()),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let new_filename = profile
        .rename_file("acquisition-2020-02-20.dcm", &dcm)
        .unwrap();

    assert_eq!(
        new_filename,
        Some("1.2.3.4.5.6.7.8.9_2020-02-20.dcm".to_string())
    );
}

#[test]
fn test_filename_rename_multiple_rules() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  filenames:
    - input-regex: '^(?P<prefix>\w+)-(?P<date>\d{4}-\d{2}-\d{2})\.dcm$'
      output: '{SOPInstanceUID}_{date}.dcm'
    - input-regex: '^(?P<uid>[\w.]+)-(?P<datetime>[\d\s:-]+)\.dcm$'
      output: '{uid}_{PatientID}.dcm'
"#;

    let tags = HashMap::from([
        ("SOPInstanceUID", "1.2.3.4.5.6.7.8.9".into()),
        ("PatientID", "PATIENT123".into()),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    // first rule matches
    let new_filename = profile
        .rename_file("acquisition-2020-02-20.dcm", &dcm)
        .unwrap();
    assert_eq!(
        new_filename,
        Some("1.2.3.4.5.6.7.8.9_2020-02-20.dcm".to_string())
    );
    // second rule matches
    let new_filename = profile
        .rename_file("1.2.3.4.5-2020-02-20 10:30:00.dcm", &dcm)
        .unwrap();
    assert_eq!(new_filename, Some("1.2.3.4.5_PATIENT123.dcm".to_string()));
}

#[test]
fn test_filename_rename_no_match() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  filenames:
    - input-regex: '^(?P<prefix>\w+)-(?P<date>\d{4}-\d{2}-\d{2})\.dcm$'
      output: '{SOPInstanceUID}_{date}.dcm'
"#;

    let tags = HashMap::from([("SOPInstanceUID", "1.2.3.4.5.6.7.8.9".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let new_filename = profile.rename_file("doesnotmatch.dcm", &dcm).unwrap();

    assert_eq!(new_filename, None);
}

#[test]
fn test_filename_rename_no_rules() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  fields:
    - name: PatientName
      replace-with: "ANON"
"#;

    let tags = HashMap::from([
        ("SOPInstanceUID", "1.2.3.4.5.6.7.8.9".into()),
        ("PatientName", "Test^Patient".into()),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let new_filename = profile.rename_file("test.dcm", &dcm).unwrap();

    assert_eq!(new_filename, None);
}

#[test]
fn test_filename_rename_path_stripped() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  filenames:
    - input-regex: '^(?P<name>\w+)\.dcm$'
      output: '{name}_{PatientID}.dcm'
"#;

    let tags = HashMap::from([("PatientID", "PAT123".into())]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();

    // Path should be stripped, only filename used for matching
    let new_filename = profile.rename_file("/path/to/file/test.dcm", &dcm).unwrap();

    assert_eq!(new_filename, Some("test_PAT123.dcm".to_string()));
}

#[test]
fn test_filename_rename_complex_template() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  filenames:
    - input-regex: '^(?P<prefix>[A-Z]+)_(?P<num>\d+)\.dcm$'
      output: '{prefix}_{StudyDate}_{SeriesNumber}_{num}_{SOPInstanceUID}.dcm'
"#;

    let tags = HashMap::from([
        ("StudyDate", "20220315".into()),
        ("SeriesNumber", 10.into()),
        ("SOPInstanceUID", "1.2.3.4.5.6.7.8.9".into()),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let new_filename = profile.rename_file("MRI_042.dcm", &dcm).unwrap();

    assert_eq!(
        new_filename,
        Some("MRI_20220315_10_042_1.2.3.4.5.6.7.8.9.dcm".to_string())
    );
}

#[test]
fn test_filename_rename_hex_format() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  filenames:
    - input-regex: '^test\.dcm$'
      output: '{00080018}_{0x00100020}.dcm'
"#;

    let tags = HashMap::from([
        ("SOPInstanceUID", "1.2.3.4.5".into()),
        ("PatientID", "PAT123".into()),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let new_filename = profile.rename_file("test.dcm", &dcm).unwrap();

    assert_eq!(new_filename, Some("1.2.3.4.5_PAT123.dcm".to_string()));
}

#[test]
fn test_filename_rename_tuple_format() {
    let yaml = r#"
version: 1
name: test profile
dicom:
  filenames:
    - input-regex: '^test\.dcm$'
      output: '{(0008, 0018)}_{(0010, 0020)}.dcm'
"#;

    let tags = HashMap::from([
        ("SOPInstanceUID", "1.2.3.4.5".into()),
        ("PatientID", "PAT123".into()),
    ]);
    let buffer = create_dcm_as_bytes(tags).expect("Failed to create DICOM");
    let dcm = buffer.get_ref().clone();

    let profile = DeidProfile::from_yaml(yaml).unwrap();
    let new_filename = profile.rename_file("test.dcm", &dcm).unwrap();

    assert_eq!(new_filename, Some("1.2.3.4.5_PAT123.dcm".to_string()));
}
