use actix_files as fs;
use actix_files::NamedFile;
use actix_web::{
    get,
    http::header::{ContentDisposition, DispositionParam, DispositionType},
    post,
    web::{self, Path},
    HttpResponse, Responder,
};
use bson::{
    doc,
    oid::{self, ObjectId},
};
use mongodb::Client;

use crate::mongo::find_one;

#[get("/file/{collection}/{id}")]
pub async fn file_by_id(
    client: web::Data<Client>,
    path: web::Path<(String, String)>,
) -> actix_web::Result<NamedFile> {
    dbg!(path.clone());
    let (collection, file_id) = path.into_inner();
    let client = client.into_inner();
    let doc = find_one(
        client,
        collection.to_string(),
        doc! {
            "_id":ObjectId::parse_str(file_id).unwrap(),
        },
    )
    .await
    .unwrap()
    .unwrap();

    let path = doc.get_str("path").unwrap();
    let file = fs::NamedFile::open(path)?;

    Ok(file
        .use_last_modified(true)
        .set_content_disposition(ContentDisposition {
            disposition: DispositionType::Attachment,
            parameters: vec![DispositionParam::Filename(
                std::path::Path::new(path)
                    .file_name()
                    .unwrap()
                    .to_str()
                    .unwrap()
                    .to_string(),
            )],
        }))
}
