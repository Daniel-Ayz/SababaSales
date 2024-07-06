<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Daniel-Ayz/SababaSales">
    <img src="images/SababaSales-logoB.png" alt="Logo" width="700" height="400">
  </a>

<h3 align="center">SababaSales</h3>

  <p align="center">
    Same as superly but better. Soon will be available online! Watch out Jeff, the sales are comming!
    <br />
    <a href="https://github.com/Daniel-Ayz/SababaSales/tree/main/docs"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Daniel-Ayz/SababaSales">View Demo</a>
    ·
    <a href="https://github.com/Daniel-Ayz/SababaSales/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/Daniel-Ayz/SababaSales/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>








<!-- GETTING STARTED -->
# Installation

### Clone the project
``` bash
git clone https://github.com/Daniel-Ayz/SababaSales.git
```

# Setup

## 🐳 Docker 
Make sure you have the following installed on your machine:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 🏛️  1. Build and start the containers
Run the following command to build and start the Docker containers:

```bash
docker-compose up --build
```
this command will:

Build the Docker images defined in the Dockerfile.
Start the services defined in the docker-compose.yml file.
we use the postgres docker image https://hub.docker.com/_/postgres.
## 📊 2. Apply Database Migrations
After the containers are up and running, you need to apply the database migrations. Open a new terminal and run(same working dir):
```bash
docker-compose exec web python manage.py makemigrations
```

```bash
docker-compose exec web python manage.py migrate
```
## 👩‍💼 3. Create a Superuser
To create a superuser for the Django admin, run the following command:
```bash
docker-compose exec web python manage.py createsuperuser
```
## 🚀 4. Access the Application
run the containers with
```bash
 docker-compose up
```
Once the containers are up and running, you can access your application at http://localhost:8000


## 🛑 5. Stopping the Application
To stop the running containers, press CTRL+C in the terminal where docker-compose up is running, or run:
```bash
docker-compose down
```

💡 if does not work - try running:
```bash
docker-compose exec web python manage.py flush
```

## 🔍 6. Monitoring Redis

To monitor the Redis cache and check the requests being made, follow these steps:

### 1. Access the Redis Container
Open a terminal and access the Redis container by running:
```bash
docker exec -it marketapi-redis-1 sh
```

### 2. Use Redis CLI to Monitor Requests
Once you are inside the Redis container, you can use the Redis CLI to monitor requests. Run the following command:
```bash
redis-cli
```

### 3. Monitor Requests
To monitor requests, run the following command in the Redis CLI:
```bash
MONITOR
```

## Useful Docker Commands
View running containers:
```bash
docker ps
```
Stop a specific container:

```bash
docker stop <container_id>
```
Start a Django shell:

```bash
docker-compose exec web python manage.py shell
```



## 🗿 Setup backend without docker
### Create a Virtualenv

- Windows

```PowerShell
  pip install virtualenv
  virtualenv .venv
  .\.venv\Scripts\activate
```


- Linux/mac

```bash
  pip install venv
  python3 -m venv .venv 
  source .venv/bin/activate
```

You may need to configure your IDE (such as VSCode) to use the virtualenv python interpreter, as well as your IDE linter.

### Install Requirements

```bash
  pip install -r requirements.txt
```

> Note: if you install new packages, please update the requirements.txt file with `pip freeze > requirements.txt`

### Install Pre-Commit Hooks

This will install pre-commit hooks that will run automatically before each commit to make sure that the code is formatted correctly and that there are no errors.

```bash
  pre-commit install
```

### Set up database
We use PostgreSQL so make sure you download it online, 
you can set it up with any password you'd like, just make sure it matches the password in `settings.py`.
in order to create a database:
```bash
  createdb -U postgres db
```

if your tests require a specific number to work, for example if the test depends on store_id being 1,
you'll need to change your test class to be as follows:
```python
class StoreAPITestCase(TransactionTestCase):
    reset_sequences = True
```
The rest is the same, define functions and test them, nocie you should only change under the circumstances mentioned
because the tests run slower this way.


### Start Up server
Initialize the database (if we don't have one already):
```bash
  cd marketapi
  python manage.py migrate
```
Start the server instance
```bash
  python manage.py runserver
```
The application should be available at [http://localhost:8000/](http://127.0.0.1:8000/api/docs) through your browser


### Setup Pycharm
Click the Python Interpreter selector and choose Add Interpreter (Add the existing one you created in the virtual environment)
https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html#python_create_virtual_env


\

# Must read docs for development

## Django
We will use the Django framework for backend [official docs](https://docs.djangoproject.com/en/5.0/intro/tutorial01/)

## Django Ninja (API)
Django Ninja is a web framework for building APIs with Django and Python 3.6+ type hints.
Make sure to read about it in the [official docs](https://django-ninja.rest-framework.com/). It supports OpenAPI (previously known as Swagger) and [JSON Schema](https://json-schema.org/), as well as [Pydantic](https://pydantic-docs.helpmanual.io/) models. It also has an ["extra" package](https://eadwincode.github.io/django-ninja-extra/) that adds some useful features.

## Pydantic
Read briefly about it in the [official docs](https://pydantic-docs.helpmanual.io/). \
We won't use it directly, but it is used by Django Ninja Schemes support.

## Tutorials

Please follow the following tutorials to get started:

- [Short Introduction to Django](https://youtu.be/nGIg40xs9e4)
- [Official Tutorial](https://django-ninja.rest-framework.com/tutorial/)
- [Django Ninja Video Tutorial](https://www.youtube.com/playlist?list=PLXskueZ7apWgNasQPt6PYhlKNKNEghT3T)
- [Django Ninja Extra Tutorial](https://eadwincode.github.io/django-ninja-extra/tutorial/)
- [Django Ninja with Pydantic](https://testdriven.io/blog/django-and-pydantic/)

### Project Examples

Please read and understand some of the following project architectures:

- [Books Example](https://github.com/ErSauravAdhikari/Karnali), only API example (good structure).
- [Blog Example](https://github.com/HyoungSooo/Django-Blog) with JWT (API), and blog (templates)
- [Django Ninja Example](https://github.com/lihuacai168/django-ninja-demo/) with some config files (such as dockerfile, env example, etc.)

### Style and Conventions Guides

- [Hitchhiker's Guide to Python](https://docs.python-guide.org/writing/style/)
- [Django Best Practices](https://medium.com/@sadhanajaiswal/django-best-practices-coding-style-7870b398889b)
- Make sure to install the pre-commit hooks as explained above.

## Feature Submissions Guidelines

1. Create an issue with the feature request on GitHub, fill in the Assignees & Projects & Milestone & Labels. [Create Issue - Enhancement](https://github.com/Daniel-Ayz/SababaSales/issues/new?labels=enhancement&template=feature-request---.md)
2. After creating the issue, Click "Create a branch" (under "Development" on the right side).
3. Run the suggested commands
```
git fetch origin
git checkout <branch-name>
```
4. Commit and push your changes frequently to the remote branch.
5. When you are done, make `git pull origin main` (to your branch) to merge the changes done in main since your branch was created. Solve conflicts carefully if there are any.  
6. Create a pull request from the remote branch to the main branch. Add the relevant reviewers and assign the pull request to yourself. Assign to the relevant milestone.
7. If the pull request is approved, it will be merged into the main branch and the remote branch will be deleted by the reviewer.

<!-- ROADMAP -->
# Roadmap

- [X] Release Version 0
    - [X] Add acceptence tests
    - [X] Add use cases
    - [X] Add class diagrams
- [ ] Release Version 1
    - [ ] Initial backend
        - [ ] Users app
            - [ ] Authentication
        - [ ] Purchase app
        - [ ] Store app
    - [ ] Initial frontend design
    - [ ] Acceptence tests (code)
- [ ] Release Version 2
- [ ] Release Version 3
- [ ] Release Final Version

See the [open issues](https://github.com/Daniel-Ayz/SababaSales/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Daniel Ayzenshteyn - ayzendan@post.bgu.ac.il  
Ron Shefland - ronshef@post.bgu.ac.il  
Daniel Erbesfeld - erbesfel@post.bgu.ac.il  
Itai Pemper - itaipem@post.bgu.ac.il  
Roy Weiss - weissroy@post.bgu.ac.il  
Roy Shvartz - royshv@post.bgu.ac.il  
Talia Katrih - katrihta@post.bgu.ac.il

Project Link: [https://github.com/Daniel-Ayz/SababaSales](https://github.com/Daniel-Ayz/SababaSales)

<p align="right">(<a href="#readme-top">back to top</a>)</p>





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/Daniel-Ayz/SababaSales.svg?style=for-the-badge
[contributors-url]: https://github.com/Daniel-Ayz/SababaSales/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Daniel-Ayz/SababaSales.svg?style=for-the-badge
[forks-url]: https://github.com/Daniel-Ayz/SababaSales/network/members
[stars-shield]: https://img.shields.io/github/stars/Daniel-Ayz/SababaSales.svg?style=for-the-badge
[stars-url]: https://github.com/Daniel-Ayz/SababaSales/stargazers
[issues-shield]: https://img.shields.io/github/issues/Daniel-Ayz/SababaSales.svg?style=for-the-badge
[issues-url]: https://github.com/Daniel-Ayz/SababaSales/issues
[license-shield]: https://img.shields.io/github/license/Daniel-Ayz/SababaSales.svg?style=for-the-badge
[license-url]: https://github.com/Daniel-Ayz/SababaSales/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/linkedin_username
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
