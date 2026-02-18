## Deploy app using Docker

We're going to deploy the app in a docker container. why?

- Consistency — same environment locally, in CI, and in production. 
  No "works on my machine" issues.                                    
  - Dependencies are locked down — Python version, system packages,   
  python packages all baked into the image. No drift.                    
  - Kubernetes needs it — you're setting up kind, so you need a       
  container image to deploy.                                          
  - Isolation — your app doesn't pollute your host system and doesn't 
  conflict with other projects (like that port 8000 collision example).
  - Reproducible builds — anyone can clone the repo and docker build
  without installing Python, uvicorn, or anything else.

## Dockerfile

RUN pip install uv
Or install from the official script:
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

I picked the first since it's more clear to a new user, and i didnt want to mess
with the path.

WORKDIR /app — sets the working directory inside the container.
  Every command after this runs from /app. Like doing cd /app but
  persistent.

  The COPY chain:
  1. COPY pyproject.toml uv.lock ./ — copies just the dependency files
   first
  2. RUN uv sync — installs dependencies
  3. COPY app/ app/ — copies your code last

## using Claude code

I'm trying to set up these examples to be the starting point for interactive questions
that'll expand your horizons.

So much of modern infrastructure is a sprawl of different technologies that are interacting
with each other, so it helps to look for the connections and patterns.

COPY app/ app/ — copies your code last

^^ let's look at this. you should be asking: why add the complexity?

I encourage you to unpeel the onion here wherever possible using Claude code.
There is a ton of depth you can get into. let's use this example of what i recommend
you do. also it deals with hallucinations pretty well :)

 > 3. COPY app/ app/ — copies your code last   <-- why do this       
  last?                                                                                                                                   
⏺ Because your code changes the most often. If you copy it earlier,   
  every code change invalidates all the layers below it — including   
  the dependency install. That means Docker re-runs uv sync every time
   you change a line of code.                                         
                                                                      
  By copying code last, a code change only rebuilds that final layer.
  Dependencies stay cached. 

> explain the layers

⏺ Each line in a Dockerfile creates a layer. Docker caches every      
  layer. When you rebuild, it starts from the top and reuses cached
  layers until it hits one that changed — then it rebuilds everything 
  from that point down.                                               
                                                                      
  So if you have:                                                     
                                                                      
  COPY pyproject.toml .   ← layer 1 (dependencies file)
  RUN uv sync             ← layer 2 (install deps)
  COPY app/ app/          ← layer 3 (your code)

  Change your code? Only layer 3 rebuilds. Change dependencies? Layers
   2 and 3 rebuild. Put them in the wrong order and you're
  reinstalling dependencies on every code change.

> ok but layers of what? 

⏺ layers of filesystem changes. Each Dockerfile    
  instruction creates a snapshot of what changed on the filesystem.
  RUN pip install uv adds files to /usr/local/bin — that diff is one  
  layer. COPY app/ app/ adds your code — that's another layer. Stack
  them all together and you get the full filesystem.

> in what format?

⏺ Tarballs. Each layer is a compressed tar archive (.tar.gz) of the   
  filesystem diff from that step.


Next steps:
Can you construct a way to see the layers?
How about making a change and seeing if the cacheing works as we described?

## try it youself + a gotcha

here's a good example to try: why is
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

broken apart instead of the full string you'd do on the command line?

note: claude doesn't do a great job of understanding the relative value of things when it
has a lot of different possible explanations. this is actually true across queries; it's 
prone to flat, thoughtless regurgiation of the same few things. for example "chatgpt knows 3 jokes"

there's a good Andrej Karpathy talk w Dwarkesh Patel about this. 

So for this particular case, see if it tells you about the main reason (imho) - the security
implications.



## run the dockerfile

1. Build the image:                                                 
  docker build -t lets-ship-it .                                      
  
  -t lets-ship-it names/tags the image. 
  . says "use the current directory as build context" (where it looks for the Dockerfile and  
  files to COPY).

  2. Run the container:
  docker run -p 8042:8000 lets-ship-it

  -p 8042:8042 maps port 8042 on your machine to port 8000 inside the
  container. Without this, the container's port is unreachable.

  3. Test it (from another terminal):
  curl http://localhost:8042/healthz

➜  lets-ship-it git:(main) ✗ curl http://localhost:8042/healthz     ()
{"status":"ok"}%   

  ➜  lets-ship-it git:(main) ✗ docker run -p 8042:8000 lets-ship-it  ()
INFO:     Started server process [10]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     192.168.65.1:33888 - "GET /healthz HTTP/1.1" 200 OK


