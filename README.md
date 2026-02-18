# Let's Ship It! A Verifiable Guide to Modern Cloud Infrastructure

## setup 
- assumes you are using python and can install things with uv
- you need to setup a KIND cluster for local k8s
- each chapter is its own branch and is additive to the next one... all the way up to main

## fire up kind k8s cluster
brew install kind
kind create cluster --name lets-ship-it
kubectl cluster-info --context kind-lets-ship-it

## Tests

### application tests
uvicorn app.main:app --port 8042
uv run pytest