### Development

* Start a local server
  ```shell
  bundle exec jekyll s
  ```

* Install dependencies listed in `Gemfile`
  ```shell
  bundle
  ```

* View all available jekyll commands
  ```shell
  bundle exec jekyll help
  ```

### Posts

* Create a new page
  ```shell
  bundle excel jekyll page "My New Page"
  ```

* Create a new post
  ```shell
  bundle exec jekyll post "My New Post"
  ```

* Create and publish a new draft
  ```shell
  bundle exec jekyll draft "My new draft"
  bundle exec jekyll publish _drafts/my-new-draft.md
  ```
