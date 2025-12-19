# vocker

## Why?

See README.

## Terminology

- image
    - A file tree representing a clean virtualenv.
    - This file tree excludes pyc files. Paths that are embedded inside files have been removed.
    - File metadata is excluded with the exception of the execute bit (which is relevant on UNIX).
    - The file tree is processed using a hash tree.
    - An image is identified by the top-level hash. This hash therefore allows someone to authenticate the entire file tree.
- container
    - An unpacked image inside a directory, ready to be used as a Python virtualenv. A container is identified by the path to its directory.
    - The same image can be unpacked into multiple containers. It's totally fine to have multiple copies of the same image for testing/development purposes.
- image tag, container tag
    - A locally-assigned name for an image or for a container. It's just a sort of alias to make it easier to refer to an image or container.

## Goals

See README.

## File locations

- IMAGES - where downloaded images/archives are stored
- CONTAINERS - where images are unpacked into directories called containers

## Example command usage
 
- `vocker image download REPO IMAGE-ID...`
    - Download files from `REPO` such that the every `IMAGE-ID` is available locally.

- `vocker image upload REPO IMAGE-ID...`
    - Upload files to `REPO` such that each `IMAGE-ID` is available remotely to other users.

- `vocker repo repack REPO (IMAGE-ID... | all)`
    - Repack the files on `REPO` such that each of `IMAGE-ID` can be downloaded independently without wasting "too much" bandwidth. If "all" is specified, then ensure that every image can be downloaded independently.

- `vocker image import --type=TYPE PATH`
    - Create a new image from the file tree at `PATH`. Return image ID of the newly-created image. The `TYPE` is either "venv" or "plain".

- `vocker image (ls | list)`
    - List the available images and their creation timestamps. Also show the current containers for each image (if any).

- `vocker container (ls | list)`
    - Does the same thing as `vocker image ls`, actually (lol).

- `vocker container create IMAGE-ID PATH`
    - Extract a fresh clean copy of the container inside `PATH`. The path is assumed to be relative to the CONTAINERS path specified in the configuration.
    - For a virtualenv this operation involves fixing some scripts which need the absolute path of the container inside of them, as well as generating or linking pyc files.

- `vocker container commit PATH`
    - Create a new image from the container at `PATH`. The type of the container is assumed to be the same as the parent container.
    - This is for lazy people who don't want to use `vocker image import --type=venv PATH`.

- `vocker container delete PATH`
    - Delete the container at `PATH`.

- `vocker fsck`
    - Check shared/deduplicated file integrity. If a file is found to have been modified (corrupted), then list every location where it exists (inside every container).

- `vocker gc`
    - Check for deleted containers and delete associated data. This includes shared pyc files that are no longer used by any container.

`vocker import -t pyenv path/`

## Concerns

### File deduplication backends

There are multiple ways of achieving file content deduplication (that is, having the exact same file contents available at multiple paths without paying multiple times the file size in storage).

This feature is needed both for deduplicating the same image file across different containers, as well as sharing pyc files across containers that have the same Python version.

Relevant filesystem features are:

- Copy-on-write file copies (reflinks)
    - This means that the file contents are initially shared between the two file "copies". If one of the copies is modified, only that section of the file is copied and modified without affecting other copy.
    - The file metadata (owning user, permissions, extended attributes) is not shared between the different copies, and can be modified independently.
    - Because this data sharing is very filesystem-specific, reflinks only work within the same filesystem. You can never make a reflink copy across two different filesystems (like a hard drive and a USB drive).
    - This sort of copy requires special filesystem support.
        - On GNU+Linux, that's bcachefs, btrfs, and XFS [(ref)](https://unix.stackexchange.com/a/631238).
        - On Windows, it's only supported on ReFS v2, which is available [only](https://github.com/0xbadfca11/reflink) on Windows Server 2016 and Windows 10 version 1703 (build 15063) or later.
        - There are no other operating systems relevant today. But if one existed, it would support it only on [APFS](https://unix.stackexchange.com/a/550932).
    - For example, let's say you're ripping your favourite BluRay movie to a high-quality mkv file, and you've produced a 20 GB file after several hours. You now want to embed a subtitle translation inside the mkv file, but you're not familiar with the tooling and you're afraid of corrupting your precious mkv file. You could make a backup copy, but that would take a long time (it's 20 GB after all). What you can do instead is `cp --reflink=always movie.mkv backup.mkv` which works instantly (since it doesn't make an actual copy), and then you can run `mkv-embed-subtitle movie.mkv my_subtitle.sub` which modifies a small part of `movie.mkv` without affecting the contents of `backup.mkv` and while still sharing most of the data between the two files.
- Symbolic links (also called "soft links" and "symlinks")
    - These are a UNIX thing, so they are natively supported on UNIX-likes like GNU+Linux and OS X.
    - A symbolic link is kind of like a shortcut to a file. It is NOT a separate copy of the file. When you open the file, the operating system automatically follows the link and opens the actual file that it points to. Opening and modifying the symbolic link actually just modifies the original file.
    - Because a symbolic link is just a shortcut containing an arbitrary path, a symbolic link can point anywhere, including locations on another filesystem.
    - Also requires special filesystem support. Symbolic links are a native UNIX feature, so they are natively supported on GNU+Linux and OS X.
        - GNU+Linux and OSX support them on all native filesystems (ext2/ext3/ext4/btrfs/etc).
        - Windows sort of supports symbolic links but may require admin privileges to enable them. They are supported on NTFS and ReFS but not on FAT16/FAT32.
- Hard links
    - Hard links are a bit weirder. Both the file contents and metadata are shared across files that are hard linked together. Metadata includes ownership, permissions, and extended attributes. Unlike symbolic links, there is no concept of link vs original file. All hard links are completely equivalent to each other.
    - Also requires special filesystem support. Hard links are a native UNIX feature, so they are natively supported on GNU+Linux and OS X.
        - On GNU+Linux and OS X, they are supported on roughly the same filesystems that also support symbolic links, which means all of the native filesystems.
        - On Windows, they are supported AND allowed by default on NTFS and probably ReFS!
            - There are some funny issues arising with hard links on Windows. For instance, Windows has extensive file locking (you can't edit a file while it's in use by another application). If a file is opened through a hard link, then it cannot be edited through another hard link, which makes sense. However, if a DLL file is hard linked and in use by a program, then you cannot delete another hard link of that file, because that counts as "editing"! The best you can do is to move the file to another location (on the same filesystem) and delete it later when it's not in use.

This [link](https://superuser.com/a/1340149) summarizes state of affairs on Windows.

No one solution fits all platforms, and different users may want different things.

| Backend           | Windows support | Linux support | Prevent accidental corruption? |
| :---------------- | :-------------- | :------------ | :----------------------------- |
| Reflinks          | very limited    | limited       | yes                            |
| Symbolic links    | no - admin only | yes           | no                             |
| Hard links        | yes             | yes           | no                             |

The item "Prevent accidental corruption" refers to whether modifying a deduplicated file also affects other deduplicated links of the same file.

A full check for corruption involves re-reading all the file data and checking the hash. However, a much faster way to check for modifications is to just look at the file [modification time](https://linux.die.net/man/2/stat) and see whether it has been modified recently. The file mtime can be set to a date far into the past (year 1970), and any change from that would indicate an accidental modification. (This quick method is not reliable against intentional modifications, because a program could also overwrite the mtime and reset it to its initial value after modifying a file.)

### pyc files

pyc files are specific to the Python version (3.9, 3.12, etc) and implementation (CPython vs PyPy). 

They should NOT be stored inside the images, and instead re-created when a container is created. This can be done by running `python -m compileall --invalidation-mode unchecked-hash <DIRECTORY>`.

#### pyc file sharing

pyc files can be pretty large overall. They should therefore be shared between containers that have the same Python version. For example, all Python 3.9 containers that have the same ".py" file in some package should share the same pyc file (using hardlinks or filesystem reflinks).

This implies a database table mapping `(python_version, source_file_hash)` to `pyc_file_hash`. You may notice that this also creates an additional annoying coupling between the image storage component and the Python containerizer.

### activation scripts

The scripts like "activate.bat" and "activate.ps1" and "activate.sh" usually embed the path to the container inside themselves. This is bad. During image creation, the paths must be removed from these files. During container creation (from an image), the paths must be put back inside the script OR an alternative relocatable script must be written instead (relocatable = you can move it elsewhere without breaking it).

### command executables

This is a unique thing on Windows, and only exists because Windows doesn't have a shebang mechanism for running scripts using an interpreter. Each of these executables is a true Windows executable with a zip archive appended at the end. The zip archive contains a script which does have a shebang, and that shebang has the container path explicit in there.

## Design ideas

This project can be largely split into two components. So much that they could arguably be put in separate packages.

### Image storage component

This manages the file tree, does hashing, implements pull/push/repack, implements hard links / CoW reflinks to save space on identical files.

### Python containerizer

This component handles two important operations:

- Turning a (venv) directory into an image. This involves removing the pyc files and removing the absolute paths inside various files.
- Turning an image into a container (venv directory). This involves re-generating the pyc files and putting back the paths inside various files.

These operations are both very Python-specific, and has not much to do with the image storage component.

## Module organization

- `dedup`: Deduplicated file storage.
    - Uses: n/a.
- `image`: Image creation and storage.
    - Provides:
        - Image creation from a venv directory.
        - Image repository format.
            - To make things very easy, the repository doesn't need to be served by a special server. Just plain static HTTP server is fine.
            - Must compress related files together (like tar.xz). This can be done simply by sorting the file list.
            - Must allow retrieving any image and its files without wasting "too much" bandwidth by downloading unwanted content. The maximum wasted bandwidth could be specified as a fixed amount when downloading an image, or as a percentage of the image content size, or both. If a "similar" image is already locally available, then this module must be able to reuse as much of the content as possible to minimize the download. This is a nontrivial CS problem, so have fun! It's a tradeoff, so let's consider a few shitty solutions:
                - Compress each content file individually.
                    - ✅ You can download any subset of the files without any "waste".
                    - ❌ The compression won't be very good because you didn't pack together related files.
                - Compress ALL of the content files together.
                    - ✅ You can download any subset of the files without any "waste".
                    - ✅ The compression will be very good (because related files got compressed together).
                    - ❌ You can't download any subset of the content efficiently.
                - Compress together the files for a given image. One image = one big compressed archive.
                    - ✅ You can download any subset of the files without any "waste".
                    - ✅ The compression will be very good (because related files got compressed together).
                    - ✅ You can download one full image without wasting any bandwidth.
                    - ❌ If you previously downloaded a nearly identical image, you still won't be able to download "just the difference".
                - Compress together the files for a given Python package by guessing from the file path. For example, all files under an image's `VENV/lib/python3.11/site-packages/waitress` are grouped together for compression.
                    - ✅ You can download any subset of the files without any "waste".
                    - ✅ The compression will be very good (because files within the same package are related and they got compressed together).
                    - ✅ You can download one full image without wasting any bandwidth.
                    - ✅ If you previously downloaded a nearly identical image, only different packages need to be downloaded.
                    - ❌ If a previously-downloaded package is really large but the new version only has a few changed files, that's still a large download.
                - Same as above, but split each group into subsets with a maximum size (e.g., 2 megabytes).
                    - ✅ You can download any subset of the files without any "waste".
                    - ✅ The compression will be very good (because files within the same package are related and they got compressed together).
                    - ✅ You can download one full image without wasting any bandwidth.
                    - ✅ If you previously downloaded a nearly identical image, only different packages need to be downloaded.
                    - ✅ If a previously-downloaded package is really large but the new version only has a few changed files, you can probably only download the affected subsets.
    - Uses:
        - `dedup` to unpack an image's files into a container directory.
        - `venv` to "fix" a newly-unpacked image so that it works correctly as a Python virtualenv, and conversely to "generalize" an existing venv so that it can be reproducibly turned into an image.
- `plugin.venv`: Virtualenv-specific stuff.
    - Uses:
        - `dedup` to efficiently store pyc files that are shared across multiple containers.

## Implementation starter notes

### Dependencies

- attrs
- marshmallow, probably

You will most likely need to keep around content indexes (which image archive file contains what data), as well as a record of which hardlink file contains which hash. The easiest way for both of these is to use a sqlite file. Either use `sqlalchemy` (a 1.4MB dependency!) as an ORM layer, or just use raw sqlite (the standard library Python module). Honestly raw sqlite isn't that bad. Using `sqlalchemy` would maybe also be a good experience. Idk.

### Virtualenv creation

To create a venv manually inside directory `./venvy/`:

    python -m venv --copies venvy

You can now "enter" the virtual environment using:

    source bin/activate   # on OSX/Linux
    Scripts\activate.bat  # on Windows

The shell will remain "activated" until it is closed. It does not affect other shells. The activation actually just modifies the "$PATH" environment variable.

You can check that `python` is now referring to the virtual environment:

    which python  # on OSX/Linux
    where python  # on Windows

You should see a path with `venvy` in it.

Note that `pip install` will, by default, download code from the internet and execute it! That's why I always use the `--no-index` flag. If you care about security and you don't want to use `--no-index`, please use a virtual machine or a docker/podman container during development, or idk use WSL2 on a Windows install you don't care about. I will be providing commands using `--no-index` because I am paranoid about security. Even the `pip download` command isn't safe, it will still sometimes execute code from the internet!

Let's add some packages to venvy! First download the latest wheel ".whl" files from:

- https://pypi.org/project/attrs/#files
- https://pypi.org/project/pure-radix/#files
- https://pypi.org/project/waitress/#files

(Just a few example packages.)

Feel free to open their contents and look inside. They're just zip archives! Place them in a directory called `./wheelhouse/`.

Now you can do something like:

    python -m pip install --no-index --find-links /path/to/wheelhouse pure-radix waitress

which will install those packages. Notice now that there is a new command `waitress-serve` available inside the virtual environment. This command is located inside the `./venvy/bin/` (UNIX) or `./venvy/Scripts/` (Windows) directory. Look at its contents.

On UNIX, it will just be a script with a shebang like "#!/path/to/venvy/bin/python".
On Windows, it will be an exe file with a zip archive appended at the end which will contain a similar shebang with double quotes around the path.

You will see a whole bunch of pyc files inside the virtualenv. You can list them using

    find -name '*.pyc'

You can get a list of all files that contain the virtualenv path explicitly using:

    find -type f -not -name '*.pyc' -print0 | xargs -0 grep -H venvy

(We're excluding the pyc files because those always contain the path.)

To turn a virtualenv into an image, all instances of the virtualenv path MUST be removed from all of the files, and all pyc files must be removed.

To turn an image back into a virtualenv, the new virtualenv root path must be embedded back into the files, and the pyc files must be regenerated.

## Repository format

To be quantitative, our goal is to efficiently deal with a 2GB virtualenv containing 100k files, and many variations of it (with slightly different package versions). Most images will share the same files.

The content hash for each file is 32-64 bytes, and the average path length seems to be about 50 characters. Maybe add one bit of metadata for the executable bit. A full index for such a virtualenv would be 10 MB in size. This is acceptable for the initial download, but not for the download of mostly-identical images.

I would prefer to avoid explicit delta compression between index files because then I have to decide how long to keep around the deltas and base files.

Maybe we can use HTTP request ranges?

### Assumptions

From image to image, most files don't change. Only some related files change together, for example when a Python package is updated.

### Idea

Given an image ID, assemble the image metadata which hashes to this image ID *and* determine which archives to fetch.

#### Image metadata resolution

The image ID is the hash of the image metadata, which contains:

- An arbitrary user-data block (probably JSON or CBOR format)
- A file dictionary {file_path: (file_metadata, file_content_hash)}

The file dictionary is very large (could be 100k entries) and only some parts of it change.

##### Image metadata compression

The image metadata is split into two files:

1. The paths and file metadata come first and are compressed together. The paths contains lots of repeated strings, so compression should be highly effective.
2. The content hash of every file, in the same order as in the previous file. Hashes are incompressible, so there's no point in even trying to compress them.

##### Variant 1: Image metadata sharding (good)

Split image metadata into multiple shards. An (overly) simple design would be that each shard gets its own compressed archive file with file contents.

But then what about deltas between archives? Maybe the client has an older archive and very little has changed since then. Each shard lists the relevant archive files, then efficiently states which archive contains which file contents. This could even be a compressed matrix bitfield. In other words, given archive index i and file content j, the entry `m[i,j]` encodes whether archive i contains file j.

##### Variant 2: Image metadata delta encoding (bad)

Compute deltas between image metadatas, and have an index file listing the available images and deltas and their sizes. The client can simply pick a favourable path through the deltas.

The delta stuff adds a lot of complexity however. It also doesn't work that well if the images are mixing and matching among package versions.

##### Hash digest swizzling

The image metadata shards contain lists of file content hashes. We can swizzle the hashes such that first we have the first byte of every content hash, then the second byte of every content hash, and so on. This allows a client to download the first few bytes of the hash for every file.

#### Server sync

When uploading a new image, a client should be aware of all of the existing images and archives on the server. This is so that it can create archives efficiently.

The easiest way is probably to just download all of the image metadata from the server. Wait but there could be files inside archives that aren't inside any image, and that are being re-added. I guess we can have a list of orphaned files in one of those image metadata shards using empty filenames.

Basically make it an invariant that we never remove image metadata shards if it would result in archive files not being listed inside any image metadata shard.

##### Sync algorithm

1. Pull all image metadata. This includes everything except archive contents.
2. Lock the remote repository by writing to "lock.txt".
3. Pull all image metadata again, in case new content was pushed before the lock was acquired.
4. Create a new catalog with an updated image list (images added or removed).
5. Create meta shards for each image, or reuse existing meta shards.
6. Create archives to contain new files that aren't in any archive yet or which would incur too large of a download cost (pulling a 5MB archive for a 10KB file) or too large of a decompression cost (1 MB archive containing 1000 versions of a library expanding to 1 GB of source code)

##### File creation algorithm

There's **a lot** of flexibility in choosing what shards and archives to create. Here's a crappy provisional draft.

- Partition the image file dictionary based off paths. Label each subset with a stable string called the "shard key".
- For each subset of the partition:
    - If there is already an existing shard with exactly the same files, then use that one and continue to the next subset in the loop.
    - Try to find a similar shard - if one exists, also create a "diff shard" which has file entries only for the files that are actually different between the older shard and the file subset.
    - (We now know what files we will have in the new shard, so what's left is archive creation.)
    - Identify archives that are quasi-subsets of this shard's files. In other words, find archives whose contents are mostly subsets of this shard's files.
    - Create a new archive containing the files that are not in any quasi-subset archive.
    - If the estimated wasted bandwidth exceeds the allowed limit, then create new archives. The new archives must support fetching any two images in succession without excessive wasted bandwidth.

###### Required queries

- Given a content hash and a repository, find all archives that contain that content.
- Given a content hash and a repository and a shard key, find all images that reference that content hash.

#### Example

```
/vocker.cbor   # Contains the vocker version, and the "project-code" and "server-code". Also contains the cryptographic hash function used for all hashes.
/current-catalog.cbor  # Current catalog index.
/manifest-history.cbor  # Top-level hash and timestamp of current and several past manifest files.
/manifest/current.bin  # List of every file path inside the repository and its hash. This is only used by the repository management stuff, not by clients that only download images.
/manifest/backup.bin  # Old manifest.
/manifest/lock.cbor  # Lock file to prevent concurrent writers from corrupting the repository. Shows who locked the repository and the lock expiration time.
/catalog/13/h.bin  # Lists the image index and image ID for all available images. Also lists the "orphan file" image metadata entries.
/image/1/is.cbor  # ID of the latest image-to-shard mapping. For example, it contains the integer 77.
/image/1/u.bin  # Contains the image "user-data".
/image/2/a.bin
...
/shard/1/p.bin  # Compressed paths and file metadata. For example, "acme/foo.txt: not executable" and "acme/bar.exe: executable"
/shard/1/h.bin  # Hash of each file content, in the same order as the file above.
/shard/1/sa.cbor  # ID of the latest shard-to-archive mapping. For example, it contains the integer 67.
/shard/5/p.zst
...
/shard/6/p.zst
...
/shard/7/p.zst
...
/sa/67/m.zst  # Contains the mapping of shard to archive for one or more shards. For example, `shard[1] = archive[23] & archive[57]`. Also contains the approximate size of each archive.
/is/15/m.zst  # Contains the mapping of image to shard for one or more images. For example, `image[1] = shard[1] & shard[5]`.
/archive/23/a.zst  # Compressed contents of multiple files. Among them is the contents of "acme/foo.txt".
/archive/23/s.zst  # Size of each of the compressed files. Compressed array of int64.
/archive/23/h.bin  # Hash of each of the compressed files.
/archive/57/a.bin  # Compressed contents of multiple files. Among them is the contents of "acme/bar.exe".
```

#### Manifest file vs hash tree

Problem: there is no way for the client to check the integrity of their download. They cannot detect a truncated or corrupted download.

One way to prevent this is to have the client download checksums. A single manifest file that contains all the checksums for all the files in a repository could end up being very large.

Another way is to arrange the file hashes in a hash tree. The client normally only downloads the leaves of the hash tree to verify its downloaded content. A developer would download the entire hash tree instead.

Either way, there's a problem with a mismatch between content and checksum when updating the content.

##### Checksum draft then content then checksum

Write procedure:

- Write all modified checksum nodes to a parallel file tree, suggestively named "/new/".
- Recursively traverse all modified directories, in a depth-first fashion:
    - Perform all content updates (generally only additions and removals, very rarely modifications of existing files).
    - Write the modified checksum nodes to the normal file tree.

Main advantage is that in case of an interrupted upload, it is easy to detect and skip directories that are finished by just reading the corresponding checksum node.

Read procedure:

- Read checksum node.
- Read file contents.
- If checksum matches, exit successfully.
- Read checksum node again, and read checksum from "new" parallel file tree. If the file contents matches neither, then exit with an error.

A great advantage is that a client knows what hash to expect and can reuse previously downloaded content.

#### Other notes

We can use the deduplication to store repository files. That way, two repositories that have (largely) the same contents won't incur twice the cost.

We should use a separate deduplication store, not together with the vocker file contents.

For cleanliness, we can keep a separate cache directory for every repository location ("project-code" + "server-code").

#### Meta-to-archive map

A meta shard has files that can be assembled from many archives. We precompute the possible ways that they can be assembled, as in:

shard1 = ((archive1 | archive2) & (archive3 | archive4 | archive5)) | archive6

If a client already has archive1 then it can pick the smallest among archive{3,4,5} and have the full file set. No need to muck about with a compressed matrix bitfield.

The shard-to-archive map must also contain the size of each of the archives to allow the client to choose the optimal archive-set to satisfy the shard file-set requirements.

Once the client chooses particular archives, then it can download the corresponding archive hash list and size list.

MVP: exactly one archive per shard.

Format:

```
[ARCHIVE_INDEX_LIST, ARCHIVE_SIZES_UINT16_BE_ARRAY, RULES_LIST]

Each rule is one of:

- ["OR", OPERANDS...]
- ["AND", OPERANDS...]
- ["OUT", OPERAND, SHARD1, SHARD2, ...]

Let n be the number of archives referenced. Then len(ARCHIVE_INDEX_LIST) = n.
Each OPERAND above is an integer k. If k>=0, then it refers to an archive by its position in the ARCHIVE_INDEX_LIST.
If k<0, then it refers to the output of the rule at index current_index+k.
```

### MVP

#### Image creation/deletion workflow

```sh
# Download the current repository state into directory "backup1". It will be good to have in case
# things go awfully wrong.
vocker repo download @my-official-repository backup1

# Make a shallow copy of "backup1" that we will make edits to.
vocker repo copy backup1 edit1

# Add the image to local repository "edit1". This reuses pre-existing metas and archives from
# "edit1" as much as possible.
vocker image import -R edit1 --type=pyenv1 /path/to/my/python/environment/

# Delete another image by ID.
vocker image delete -R edit1 01234567

# Export an image out of a local repository for testing.
vocker image export -R edit1 /path/to/new/python/env/

# Export an image out of a remote repository for testing.
vocker image export -R @my-other-official-repository /path/to/new/python/env/

# Repack repository and delete archives.
vocker repo repack edit1

# Push the changes to the remote repository.
# This is fast because it simply compares the local "manifest.bin" with the remote "manifest.bin".
# If the remote repository has changed since we downloaded it, show an error and tell the user to
# use the --force flag if they really want to squash whatever remote changes have occurred.
vocker repo upload edit1 @my-official-repository
```
