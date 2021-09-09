[![CI-test](https://github.com/yugaWicaksono/taskmaster_fastapi/actions/workflows/test-build.yml/badge.svg)](https://github.com/yugaWicaksono/taskmaster_fastapi/actions/workflows/test-build.yml)

# Taskmaster API (FastAPI + mongoDB) v.0.2

This is my first time building an API using FastAPI and MongoDB. Also, the first experience I have with these both
technologies. I recommend using FastAPI, if you want to build an API quickly and has a good knowledge of python.

Initially, coded following instruction `Tech With Tim` on Youtube
[https://www.youtube.com/watch?v=-ykeT6kk4bk&t=1290s]. Though, it is now my own implementation with checking of token
signature, 2-token verification and the Google cloud run implementation.

## Required packages

     1. fastapi~=0.68.0
     2. uvicorn~=0.15.0
     3. pymongo~=3.12.0
     4. python-decouple~=3.4
     5. pydantic~=1.8.2
     6. starlette~=0.14.2
     7. gunicorn
     8. pymongo[srv]
     9. pyjwt~=2.1.0
     10. icecream~=2.1.1
     11. pytest
     12. pytest-asyncio
     13. httpx

## MongoDB

If you want to try this project the MongoDB setup is up to you. I recommend using MongoDB Atlas. It is still within the
free tier range as the data generated is not much.




