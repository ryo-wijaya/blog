## Folder Structure Overview

Here’s a breakdown of the most important folders and files in this repository:

### Root Directory

- **`_config.yml`**: Main configuration file for the Jekyll site. This is where you configure site-wide settings like title, description, theme options, and plugins.
- **`Gemfile`**: Specifies Ruby gem dependencies, such as Jekyll and Chirpy theme. Useful for managing local development environments.

### `_posts/`

- Contains your blog posts in markdown format. Each post should follow the `YYYY-MM-DD-title.md` naming convention. You can categorize and tag posts via the front matter.

### `_tabs/`

- Contains the content for static pages (e.g., `about`, `categories`, and `tags`). You can customize or add new tabs here to appear in the navigation bar.
  - **`about.md`**: Modify this to update your "About" page.
  - **`tags.html`** and **`categories.html`**: Control the layout of the tags and categories pages.

### `_data/`

- Stores YAML files that provide data to be used in the site. You can define structured content like social media links or contributors here.
  - **`social.yml`**: Customize your social media links and icons that appear in the footer.

### `_includes/`

- Contains reusable HTML snippets (partials) used across the site.
  - **Header and Footer**: Includes the HTML for the header and footer sections of the site.
  - **`meta.html`**: Manages SEO-related tags for better search engine visibility.

### `_layouts/`

- Defines the structure of your pages. Customizing layouts allows you to change the overall structure of posts, pages, and other content.
  - **`post.html`**: The layout for individual blog posts.
  - **`page.html`**: The layout for static pages like "About".

### `assets/`

- Stores site assets such as images, JavaScript, CSS, and fonts. You can organize them in subdirectories.
  - **`img/`**: Store images used in your site here.
  - **`js/`**: Contains JavaScript files.
  - **`css/`**: Contains any custom CSS styles.

### `plugins/`

- Optional Jekyll plugins used by Chirpy for additional functionality. Manage plugins via the `Gemfile`.
