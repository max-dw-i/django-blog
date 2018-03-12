## Blog on Django

A simple blog application implemented with Django framework.


## Main implemented features

+ User accounts, authentication, simple account settings, password reset;
+ Comments for authenticated users;
+ Admin interface for managing posts, users, comments;
+ Form for sending emails to the blog's author;
+ Simple search,
+ Some CSS,
+ A few unit tests.

## Installation

To use locally, do the next things:

```bash
# Clone the repository
git clone git@github.com:oratosquilla-oratoria/django-blog.git
# Install the requirements
pip install -r requirements.txt
# Setup the configuration
cp .env.local .env
# Create a database
python manage.py migrate
# Run the development server
python manage.py runserver
```

The project will be available at **127.0.0.1:8000**


## License

The source code is released under the MIT License.
