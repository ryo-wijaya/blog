import sys
import os
from datetime import datetime, timedelta, timezone

# Check if a title is provided
if len(sys.argv) < 2:
    print('Usage: python new_post.py "Post Title"')
    sys.exit(1)

# Variables
title = sys.argv[1]
slug = title.lower().replace(" ", "-")

# Generate date with the correct format and timezone (+0800)
sgt = timezone(timedelta(hours=8))  # Singapore Time (+0800)
date = datetime.now(sgt).strftime("%Y-%m-%d %H:%M:%S %z")
filename = f"_posts/{datetime.now(sgt).strftime('%Y-%m-%d')}-{slug}.md"

# Front matter template with image options
front_matter = f"""---
layout: post
title: "{title}"
description: >-
  Your description here
author: ryo
date: {date}
categories: [Category1, Category2]
tags: [tag1, tag2]
image:
  path: assets/img/<slug>/<file>
  alt: A description of the image
show_image_in_post: true
toc: true
comments: false
pin: false
published: false
---
"""

# Write to the file
os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, "w") as f:
    f.write(front_matter)

print(f"New post created: {filename}")
