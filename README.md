# Semantic-Digital-Library-Project

Project for the Semantic Digital Libraries course | UNIBO | Digital Humanities and Digital Knowledge

It is a proof concept for a GraphRAG system, leveraging linkable entities to perform SPARQL queries on a graph database based on RDF.

Visit the GitBook with our documentation: https://kr-and-e-2023-4-controversy-abou.gitbook.io/library-system-dude-kg-and-llm-for-libraries/

# Requirements

To run the code, these are some requirements:

* Docker installed on your machine for quick GraphDB setuo.

* Have an [OpenRouter](https://openrouter.ai/) API key (a free tier is available, without having to submit a payment method) for remote LLM calls.

* Have Ollama installed for local LLM calls.

# Instructions

The code entry point is the lsd.py file. To run it correctly:

* install all the necessary packages from the requirements: ´pip install -r requirements.txt´

* run the following terminal command to instantiate a graphdb instance (**Docker required**):

    **Unix / macOS**
    <pre><code>docker pull ontotext/graphdb:11.0.1 &amp;&amp; \ 
        docker run -d --name graphdb \ 
        -p 7200:7200 \ 
        ontotext/graphdb:11.0.1 &amp;&amp; 
        \ open http://localhost:7200</code></pre>

    **Windows CMD**
    <pre><code>docker pull ontotext/graphdb:11.0.1 &amp;&amp; ^ 
        docker run -d --name graphdb ^
        -p 7200:7200 ^ 
        ontotext/graphdb:11.0.1 &amp;&amp; ^ 
        start http://localhost:7200 </code></pre>


* from the GraphDB GUI, import *dataFinal.ttl* in the import menu; then go to 'Setup' and create a new repo. Ensure it is up and running.

* if you intend to use an API key: 
    + create a .env file in the same directory;
    * setup a key-values pair like this ´API_KEY=your-key´;

* if you intend to run a local LLM:
    * ensure Ollama is running: run ´ollama serve´
    * pull your model of choice from Ollama: ´ollama pull model-name´


