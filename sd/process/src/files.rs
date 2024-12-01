use anyhow::{Ok, Result};
use async_recursion::async_recursion;
use dashmap::DashMap;
use futures::future::join_all;
use rayon::iter::{
    IntoParallelRefIterator, IntoParallelRefMutIterator, ParallelBridge, ParallelIterator,
};
use std::{
    collections::HashMap,
    fs::{metadata, read_dir},
    sync::{Arc, Mutex},
    vec,
};
use tokio::{fs::ReadDir, spawn, task::JoinHandle};

pub async fn get_dir_contents(dir_path: &str) -> Result<Vec<String>> {
    if !metadata(dir_path).unwrap().is_dir() {
        return Ok(vec![dir_path.to_string()]);
    }

    let mut contents: Vec<String> = Vec::new();
    let paths = read_dir(dir_path).unwrap();

    for dir_entry in paths {
        if dir_entry.is_err() {
            continue;
        }
        contents.push(dir_entry.unwrap().path().display().to_string());
    }

    return Ok(contents);
}

/**
 * Inputs a directory path and it provides all the file paths present in it
 * NOTE:
 * This would return the relative paths of the files
 */
#[async_recursion]
pub async fn recursive_get_contents(dir_path: &str) -> Result<Vec<String>> {
    let mut files = Vec::new();
    let contents = get_dir_contents(dir_path).await.unwrap();
    for path in contents {
        if metadata(path.clone()).unwrap().is_dir() {
            files.append(&mut recursive_get_contents(path.as_str()).await.unwrap());
        } else {
            files.push(path);
        }
    }
    return Ok(files);
}

/**
 * Gives all the fits file paths in the given dir_path
 */
#[async_recursion]
pub async fn get_all_fits_files(dir_path: String, contents: Arc<Mutex<Vec<String>>>) -> Result<()> {
    let mut spawns = Vec::new();

    let paths = read_dir(dir_path).unwrap();

    for dir_entry in paths {
        let path = dir_entry.unwrap().path().display().to_string();
        if metadata(path.clone()).unwrap().is_dir() {
            spawns.push(spawn(get_all_fits_files(path, contents.clone())));
        } else if path.ends_with(".fits")
            || path.ends_with(".sa")
            || path.ends_with(".hk")
            || path.ends_with(".pha")
            || path.ends_with(".gti")
            || path.ends_with(".lc")
        {
            println!("| FOUND | {:?}", path.clone());
            contents.lock().unwrap().push(path);
        }
    }

    join_all(spawns).await;

    Ok(())
}

#[async_recursion]
pub async fn get_all_file_ext(dir_path: String, exts: Arc<DashMap<String, bool>>) -> Result<()> {
    let mut spawns = Vec::new();

    let paths = read_dir(dir_path).unwrap();

    for dir_entry in paths {
        let path = dir_entry
            .as_ref()
            .unwrap()
            .path()
            .clone()
            .display()
            .to_string();
        if metadata(path.clone()).unwrap().is_dir() {
            spawns.push(spawn(get_all_file_ext(path, exts.clone())));
        } else {
            let path_clone = dir_entry.unwrap().path().clone();
            let ext = path_clone.extension();
            if ext.is_some() {
                let ext_string = ext.unwrap().to_str().unwrap().to_string();
                if !exts.contains_key(&ext_string) {
                    println!("| FOUND EXT | {:?}  {:?}", ext_string.clone(), path);
                    exts.insert(ext_string, true);
                }
            }
        }
    }

    join_all(spawns).await;

    Ok(())
}
