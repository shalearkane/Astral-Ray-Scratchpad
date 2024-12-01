use std::{fs::File, path::PathBuf, str::FromStr};

use anyhow::Result;
use ripunzip::{NullProgressReporter, UnzipEngine};
use tokio::fs::remove_file;

pub async fn unzip_file(file_path: String, dest_dir: String) -> Result<Vec<String>> {
    let file = File::open(file_path.clone()).unwrap();
    let engine = UnzipEngine::for_file(file.try_clone().unwrap()).unwrap();
    let files = UnzipEngine::for_file(file).unwrap().list().unwrap();
    let mut file_list = vec![];
    for file in files {
        if file.contains(".") {
            file_list.push(format!("{dest_dir}/{file}"));
        }
    }

    engine
        .unzip(ripunzip::UnzipOptions {
            filename_filter: Option::None,
            output_directory: Some(PathBuf::from_str(dest_dir.as_str()).unwrap()),
            password: Option::None,
            progress_reporter: Box::new(NullProgressReporter),
            single_threaded: false,
        })
        .unwrap();

    remove_file(file_path).await.unwrap();

    Ok(file_list)
}
