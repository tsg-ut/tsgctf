#[macro_use]
extern crate serde_derive;

use hex;
use std::io::prelude::*;
use std::fs::File;
use crc::{Hasher32, crc32};
use bincode::{serialize};
use crypto::digest::Digest;
use crypto::sha1::Sha1;

#[derive(Serialize, Debug)]
struct FileHeader {
    head_type: u8,
    head_flags: u16,
    head_size: u16,
    pack_size: u32,
    unp_size: u32,
    host_os: u8,
    file_crc: u32,
    ftime: u32,
    unp_ver: u8,
    method: u8,
    name_size: u16,
    attr: u32,
}

#[derive(Serialize, Debug)]
struct LargeHeader {
    high_pack_size: u32,
    high_unp_size: u32,
}

fn get_byte(x: u32) -> u8 {
    let x: u32 = ((48271_u64 * x as u64) % 0x7fffffff) as u32;
    let x = (x << 13) ^ x;
    let x = (x >> 17) ^ x;
    let x = (x << 5) ^ x;
    (x & 0xff) as u8
}

static FILESIZES: &'static [u64] = &[
    1337,
    0x3bc0,
    0x2edcf,
    0x7f72,
    0x1d8b0,
    0x10f,
    0xc1b42,
    0x37811,
    0x34cc9,
    0xffb4f,
    0xd8639,
    0x68682a4,
    0x81ba867,
    0xe3794b,
    0x783c3b72,
    0xdf332b0a,
    0x3a8ec06a,
    0x96ae1,
    0xec240ad4,
    1337,
    1337,
    1337,
    0x3f8847bc1,
    0x54cc61a1d,
    0x4bffff74,
    0x68f2da05,
    0x14a0d6e99,
    0x3760,
    0x98da915,
    0x553ee22a7,
    0xf1b5b293,
    1337,
    0xf67e5cb5,
    0xb7249,
    0xf5b6646,
    0x4dff5d,
    1337,
    0x2190393b0f,
    0x24ca43ad3,
    0xd74bfc99,
    0x86c8b464,
    0xfb111c7b,
    0x1e81102,
    0xd9eaf2bdb,
    0x1ffb8b17e,
    0x6a8849,
    0xc72177,
    0xb9ecd0,
    0x2a2ad0,
];

// static PIECESIZE: u64 = 65536;
static PIECESIZE: u64 = 16777216;

fn main() -> std::io::Result<()> {
    let mut hasher = Sha1::new();

    // let mut buffer = File::create("temp.rar")?;
    let mut offset: u64 = 0;

    let starter = [0x52, 0x61, 0x72, 0x21, 0x1A, 0x07, 0x00, 0xCF, 0x90, 0x73, 0x00, 0x00, 0x0D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00];
    // buffer.write(&starter)?;
    hasher.input(&starter);
    offset += starter.len() as u64;
    println!("starter: {}", hex::encode(starter));

    for i in 0..FILESIZES.len() {
        let initial_offset = offset;
        let file_size = FILESIZES[i];
        let file_name = format!("dummy{:>05}\0", i + 1);
        let mut digest = crc32::Digest::new(crc32::IEEE);
        for j in 0..file_size {
            digest.write(&[get_byte(((offset + 47_u64 + j) % 0xe9cc19e1_u64) as u32)]);
            if j & 0xffffffff == 0xffffffff {
                println!("progress: {:X}", j);
            }
        }
        let file_crc = digest.sum32();

        let file_header = FileHeader {
            head_type: 0x74,
            head_flags: if file_size >= 0x100000000 {0x9120} else {0x9020},
            head_size: if file_size >= 0x100000000 {0x24 + 8} else {0x24} + file_name.len() as u16,
            pack_size: file_size as u32,
            unp_size: file_size as u32,
            host_os: 0x02,
            file_crc: file_crc,
            ftime: 0x4e88acf4,
            unp_ver: 29,
            method: 0x30,
            name_size: file_name.len() as u16 - 1,
            attr: 0x20,
        };
        let mut header: Vec<u8> = serialize(&file_header).unwrap();

        if file_size >= 0x100000000 {
            let large_header = LargeHeader {
                high_pack_size: (file_size >> 32) as u32,
                high_unp_size: (file_size >> 32) as u32,
            };
            let large: Vec<u8> = serialize(&large_header).unwrap();
            header.extend(large);
        }

        header.extend(file_name.bytes());
        header.extend(&[0xF0, 0xB5, 0x23, 0x82]);

        let header_crc = crc32::checksum_ieee(&header);

        let mut chunk: Vec<u8> = vec![
            (header_crc & 0xff) as u8,
            ((header_crc >> 8) & 0xff) as u8,
        ];
        chunk.extend(&header);

        if (offset / PIECESIZE) == ((offset + chunk.len() as u64) / PIECESIZE) {
            hasher.input(&chunk);
        } else {
            let fill_size: usize = ((offset / PIECESIZE + 1) * PIECESIZE - offset) as usize;
            hasher.input(&chunk[..fill_size]);
            println!("piece_hash[{}]: {}", offset / PIECESIZE, hasher.result_str());
            hasher = Sha1::new();
            hasher.input(&chunk[fill_size..]);
        }

        offset += chunk.len() as u64;

        // buffer.write(&chunk)?;

        for j in 0..file_size {
            let byte = get_byte(((offset + j) % 0xe9cc19e1_u64) as u32);
            hasher.input(&[byte]);
            // buffer.write(&[byte])?;
            if (offset + j + 1) % PIECESIZE == 0 {
                println!("piece_hash[{}]: {}", (offset + j + 1) / PIECESIZE - 1, hasher.result_str());
                hasher.reset();
            }
        }

        println!("chunk[{}]: {}", i, hex::encode(chunk));
        println!("offset[{}]: {}", i, initial_offset);

        offset += file_size;

        if i == 40 {
            println!("flag_offset: {}", offset);
            let mut f = File::open("flag.rar")?;
            let mut flag_buffer = Vec::new();
            f.read_to_end(&mut flag_buffer)?;
            if (offset / PIECESIZE) == ((offset + flag_buffer.len() as u64) / PIECESIZE) {
                hasher.input(&flag_buffer);
            } else {
                let fill_size: usize = ((offset / PIECESIZE + 1) * PIECESIZE - offset) as usize;
                hasher.input(&flag_buffer[..fill_size]);
                println!("piece_hash[{}]: {}", offset / PIECESIZE, hasher.result_str());
                hasher.reset();
                hasher.input(&flag_buffer[fill_size..]);
            }
            offset += flag_buffer.len() as u64;
        }
    }

    let terminator = [0xC4, 0x3D, 0x7B, 0x00, 0x40, 0x07, 0x00];
    println!("terminator: {}", hex::encode(terminator));
    // buffer.write(&terminator)?;
    if (offset / PIECESIZE) == ((offset + terminator.len() as u64) / PIECESIZE) {
        hasher.input(&terminator);
    } else {
        let fill_size: usize = ((offset / PIECESIZE + 1) * PIECESIZE - offset) as usize;
        hasher.input(&terminator[..fill_size]);
        println!("piece_hash[{}]: {}", offset / PIECESIZE, hasher.result_str());
        hasher.reset();
        hasher.input(&terminator[fill_size..]);
    }
    offset += terminator.len() as u64;
    println!("piece_hash[{}]: {}", offset / PIECESIZE, hasher.result_str());
    println!("file_size: {}", offset);
    Ok(())
}
