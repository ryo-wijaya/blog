---
layout: post
title: "Linux Cheatsheet"
description: >-
  Personal Linux cheatsheet. Covers navigation, file ops, text processing, permissions, processes, networking, disk, users, package managers, environment, archiving, system info, and pipes/redirection.
author: ryo
date: 2023-09-10 16:03:45 +0800
categories: [Software Engineering]
tags: [linux, cheatsheet]
toc: true
comments: true
pin: false
published: true
---

## 1. Navigation and File Operations

```bash
pwd                        # print working directory
ls -lah                    # list with human-readable sizes, hidden files
cd -                       # go back to previous directory
mkdir -p a/b/c             # create nested dirs
cp -r src/ dst/            # copy directory recursively
mv old.txt new.txt         # rename or move
rm -rf dir/                # delete directory recursively (no confirmation)
ln -s /path/to/target link # create symlink
ln /path/to/target hard    # create hard link
```

### find

`find` traverses the filesystem recursively from the given path. Use `-exec` or `-delete` to act on results directly.

```bash
find . -name "*.log"                      # find by name (recursive)
find . -type f -name "*.txt"              # files only
find . -type d -name "cache"              # directories only
find . -mtime -7                          # modified within last 7 days
find . -size +100M                        # files larger than 100MB
find . -name "*.tmp" -delete              # find and delete
find . -name "*.java" -exec grep -l "TODO" {} \;   # find files matching grep
```

---

## 2. File Viewing and Searching

```bash
cat file.txt               # print entire file
less file.txt              # page through file (q to quit, /pattern to search)
head -n 20 file.txt        # first 20 lines
tail -n 50 file.txt        # last 50 lines
tail -f app.log            # follow live output

wc -l file.txt             # count lines
wc -w file.txt             # count words
```

### grep

`grep` filters lines matching a regex pattern. Combine `-r`, `-n`, and `-l` for recursive searches with line numbers and filename-only output.

```bash
grep "error" app.log                  # search for pattern
grep -i "error" app.log               # case-insensitive
grep -r "TODO" src/                   # recursive search in directory
grep -n "error" app.log               # show line numbers
grep -v "debug" app.log               # invert match (exclude lines)
grep -E "error|warn" app.log          # extended regex (OR)
grep -A 3 "error" app.log             # show 3 lines after match
grep -B 3 "error" app.log             # show 3 lines before match
grep -C 3 "error" app.log             # show 3 lines before and after
grep -l "TODO" src/**/*.java          # print only filenames with match
grep -c "error" app.log               # count matching lines
```

---

## 3. Text Processing

### sed (stream editor)

```bash
sed 's/foo/bar/' file.txt             # replace first occurrence per line
sed 's/foo/bar/g' file.txt            # replace all occurrences
sed -i 's/foo/bar/g' file.txt         # in-place edit
sed -n '5,10p' file.txt               # print lines 5 to 10
sed '/^#/d' file.txt                  # delete comment lines
sed 's/^[[:space:]]*//' file.txt      # trim leading whitespace
```

### awk

```bash
awk '{print $1}' file.txt             # print first field (space-delimited)
awk -F',' '{print $2}' file.csv       # comma-delimited, print second column
awk '{sum += $1} END {print sum}' f   # sum first column
awk 'NR==5' file.txt                  # print line 5
awk 'NR>=5 && NR<=10' file.txt        # print lines 5-10
awk '$3 > 100 {print $1}' file.txt    # conditional: print $1 where $3 > 100
awk -F':' '{print $1}' /etc/passwd    # list all usernames
```

### cut, sort, uniq

```bash
cut -d',' -f1,3 file.csv             # extract columns 1 and 3
cut -c1-10 file.txt                  # extract characters 1 to 10

sort file.txt                         # alphabetical sort
sort -n file.txt                      # numeric sort
sort -r file.txt                      # reverse sort
sort -k2 file.txt                     # sort by second field
sort -t',' -k2 -n file.csv           # sort CSV by second column numerically

uniq file.txt                         # remove consecutive duplicates
sort file.txt | uniq                  # remove all duplicates
sort file.txt | uniq -c               # count occurrences
sort file.txt | uniq -d               # show only duplicates
```

---

## 4. Permissions and Ownership

```bash
chmod 755 file.sh                     # rwxr-xr-x
chmod +x file.sh                      # add execute for all
chmod -R 644 dir/                     # recursive, all files rw-r--r--
chown user:group file.txt             # change owner and group
chown -R user:group dir/              # recursive
```

### Permission Bits

Permissions are three octal digits for owner, group, and other. Each digit is the sum of read (4), write (2), and execute (1).

```
rwxrwxrwx
||||||||| 
||||||+++-- other (world)
|||+++------ group
+++--------- owner (user)

r = 4
w = 2
x = 1

755 = rwxr-xr-x  (owner: full, group/other: read+execute)
644 = rw-r--r--  (owner: read+write, group/other: read only)
600 = rw-------  (owner only)
777 = rwxrwxrwx  (everyone full - avoid)
```

### umask

`umask` sets the default permission mask for newly created files and directories. It subtracts from 666 (files) and 777 (dirs).

```bash
umask              # show current umask (e.g., 022)
umask 027          # set umask: new files = 640, new dirs = 750
# umask subtracts from 666 (files) and 777 (dirs)
# umask 022: files = 666-022 = 644, dirs = 777-022 = 755
```

---

## 5. Process Management

```bash
ps aux                         # all processes (BSD style)
ps -ef                         # all processes (POSIX style)
ps -ef | grep java             # find java processes

top                            # live process view
htop                           # better top (if installed)

kill 1234                      # send SIGTERM to PID
kill -9 1234                   # send SIGKILL (force kill)
killall java                   # kill all processes named "java"
pkill -f "myapp.jar"           # kill by full command match

jobs                           # list background jobs in current shell
bg %1                          # resume job 1 in background
fg %1                          # bring job 1 to foreground
Ctrl+Z                         # suspend foreground process
Ctrl+C                         # send SIGINT to foreground process

nohup ./script.sh &            # run detached from terminal, output -> nohup.out
nohup ./script.sh > out.log 2>&1 &   # custom output file
```

---

## 6. Networking

```bash
# curl
curl https://api.example.com/users               # GET
curl -X POST -H "Content-Type: application/json" \
     -d '{"name":"ryo"}' https://api.example.com/users  # POST
curl -o output.tar.gz https://example.com/file.tar.gz   # download to file
curl -I https://example.com                       # headers only
curl -u user:pass https://api.example.com         # basic auth
curl -L https://example.com                       # follow redirects

# wget
wget https://example.com/file.tar.gz             # download file
wget -r -np https://example.com/docs/            # recursive download

# Socket stats
ss -tulnp                     # listening TCP/UDP ports with process info
ss -tnp                       # established TCP connections with process info
netstat -tulnp                # same as ss -tulnp (older systems)

# SSH
ssh user@host                         # connect
ssh -i key.pem user@host              # with key file
ssh -p 2222 user@host                 # custom port
ssh -L 8080:localhost:8080 user@host  # local port forward

# SCP / rsync
scp file.txt user@host:/path/         # copy file to remote
scp -r dir/ user@host:/path/          # copy directory to remote
rsync -avz src/ user@host:/dst/       # sync with compression
rsync -avz --delete src/ user@host:/dst/   # sync and delete extra files on remote
```

---

## 7. Disk and Storage

```bash
df -h                         # disk usage per filesystem, human-readable
df -h /var                    # disk usage for specific mount point

du -sh dir/                   # total size of directory
du -sh *                      # size of each item in current directory
du -sh * | sort -h            # sorted by size

lsblk                         # list block devices (disks, partitions)
lsblk -f                      # include filesystem type and UUID
```

---

## 8. Users and Groups

```bash
whoami                        # current user
id                            # uid, gid, groups for current user
groups user                   # groups a user belongs to

useradd -m -s /bin/bash ryo  # create user with home dir and bash shell
passwd ryo                    # set password
usermod -aG docker ryo        # add user to group (append, don't replace)
userdel -r ryo                # delete user and home directory

groupadd devs                 # create group
groupdel devs                 # delete group

sudo command                  # run as root
sudo -u postgres psql         # run as another user
sudo su -                     # switch to root shell
visudo                        # edit /etc/sudoers safely
```

---

## 9. Package Management

The correct package manager depends on the Linux distribution:

| Distro Family | Examples | Package Manager | Install command |
|---|---|---|---|
| Debian/Ubuntu | Ubuntu, Debian | `apt` | `apt install pkg` |
| RHEL/CentOS | RHEL, CentOS, Fedora, Amazon Linux | `yum` or `dnf` | `yum install pkg` |
| Alpine | Alpine Linux (common in Docker) | `apk` | `apk add pkg` |

### apt (Debian/Ubuntu)

```bash
apt update                        # refresh package index
apt upgrade                       # upgrade all installed packages
apt install curl git              # install packages
apt remove curl                   # remove package (keep config)
apt purge curl                    # remove package and config
apt search nginx                  # search for package
apt show nginx                    # package details
apt list --installed              # list installed packages
```

### yum / dnf (RHEL/CentOS/Fedora)

```bash
yum update                        # update all packages
yum install curl git              # install
yum remove curl                   # remove
yum search nginx                  # search
yum info nginx                    # package details
dnf install curl                  # dnf is yum's successor (Fedora, RHEL 8+)
```

### apk (Alpine)

Alpine is common in Docker base images (`FROM alpine:3.19`). Alpine containers are minimal - many tools are absent and need to be installed.

```bash
apk update                        # refresh index
apk add curl git bash             # install (no confirmation prompt)
apk del curl                      # remove
apk search nginx                  # search
apk info curl                     # package details
apk add --no-cache curl           # install without caching index (common in Dockerfiles)
```

---

## 10. Environment and Shell

```bash
export VAR=value                  # set environment variable
echo $VAR                         # print variable
unset VAR                         # remove variable
env                               # list all environment variables
printenv PATH                     # print specific env var

# PATH manipulation
export PATH=$PATH:/usr/local/bin

alias ll='ls -lah'                # define alias (current session only)
alias                             # list all aliases

# Persistent config
# bash: ~/.bashrc or ~/.bash_profile
# zsh:  ~/.zshrc
source ~/.bashrc                  # reload config without restarting shell

which python3                     # find executable location
type python3                      # same but also shows aliases/builtins
```

---

## 11. Archiving and Compression

```bash
# tar
tar -czf archive.tar.gz dir/      # create gzip archive
tar -cjf archive.tar.bz2 dir/     # create bzip2 archive
tar -xzf archive.tar.gz           # extract gzip archive
tar -xzf archive.tar.gz -C /dst/  # extract to specific directory
tar -tzf archive.tar.gz           # list contents without extracting

# gzip
gzip file.txt                     # compress (replaces original with file.txt.gz)
gzip -d file.txt.gz               # decompress
gunzip file.txt.gz                # same as gzip -d

# zip
zip -r archive.zip dir/           # create zip
unzip archive.zip                 # extract
unzip archive.zip -d /dst/        # extract to directory
unzip -l archive.zip              # list contents
```

---

## 12. System Information

```bash
uname -a                          # kernel name, version, arch
uname -r                          # kernel version only
cat /etc/os-release               # distro name and version

uptime                            # how long system has been running, load averages
free -h                           # memory usage (RAM + swap), human-readable

lscpu                             # CPU info (cores, architecture, speed)
nproc                             # number of available processing units

lsof -i :8080                     # what process is listening on port 8080
lsof -p 1234                      # all files opened by PID 1234
lsof -u ryo                       # all files opened by user ryo
```

---

## 13. Redirection, Pipes, and One-liners

```bash
# Redirection
command > file.txt                # stdout to file (overwrite)
command >> file.txt               # stdout to file (append)
command 2> error.txt              # stderr to file
command 2>&1                      # redirect stderr to stdout
command > out.txt 2>&1            # both stdout and stderr to file
command < input.txt               # stdin from file

# Pipes
ps aux | grep java                # pipe stdout of ps to grep
cat access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -20

# xargs
find . -name "*.log" | xargs rm -f           # delete found files
find . -name "*.java" | xargs grep -l "TODO" # grep in found files
echo "a b c" | xargs -n1 echo               # one arg per line

# tee
./script.sh | tee output.log               # write to file AND stdout
./script.sh 2>&1 | tee output.log          # both streams

# watch
watch -n 5 'df -h'               # re-run command every 5 seconds
watch -n 1 'ss -tulnp'           # watch open ports

# crontab
crontab -l                       # list cron jobs
crontab -e                       # edit cron jobs
# Format: minute hour day-of-month month day-of-week command
0 2 * * * /home/ryo/backup.sh    # run daily at 02:00
*/5 * * * * /home/ryo/check.sh   # run every 5 minutes
```
