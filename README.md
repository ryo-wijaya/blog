### Info

This blog runs on Jekyll, Liquid templates for layouts, and GitHub Actions and Pages for deployment and hosting. It utilizes the open-source Chirpy Jekyll Theme.

[![Visit Blog](https://img.shields.io/badge/Visit-%20Blog-brightgreen?style=for-the-badge)](https://blog.ryo-wijaya.me)

### Posts

- Create a new post (using jekyll compose)

  ```shell
  bundle exec jekyll post "My New Post"
  ```

- Create a new post with template Front Matter (using custom python script)

  ```shell
  python new_post.py "Post Title"
  ```

### Development

- Start a local server

  ```shell
  bundle exec jekyll s
  ```

- Start a local server with draft posts seen as published

  ```shell
  bundle exec jekyll s --drafts
  ```

- Clean and build

  ```shell
  bundle exec jekyll clean
  bundle exec jekyll build
  ```

- View all available jekyll commands
  ```shell
  bundle exec jekyll help
  ```
