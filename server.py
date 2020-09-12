import flask
from flask import request
from censys_subdomain_finder import get_subdomains_for_api

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    
    if 'domain' in request.args:
        domain = request.args['domain']
        subdomains = get_subdomains_for_api(domain)
        return "Got sub-Domains - \n {}".format(subdomains)
    else:
        return "Error: No domain field provided. Please specify an domain."


    

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)