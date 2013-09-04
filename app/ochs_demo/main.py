import webapp2, json, markdown2, httplib2, re
from boto.s3.connection import S3Connection
from boto.s3.key import Key

class MainPage(webapp2.RequestHandler):
  
  def get(self):
    self.response.headers['Content-Type'] = "text/plain"
    self.response.write('Hello OCHS Demo')

class CommitHandler(webapp2.RequestHandler):

  def __init__(self, request, response):
    # Set self.request, self.response and self.app.
    self.initialize(request, response)
    self.http = httplib2.Http()
    self.markdowner = markdown2.Markdown()
    s3_connection = S3Connection('AKIAJHLNZALHW3YDAJXA', 'g4q+5iQPBR4tIiWxtgDLkQlCK77x5D+TFYLcsbXe')
    self.s3 = s3_connection.get_bucket('ochs_demo')

  def post(self):
    json_data = json.loads(self.request.get('payload'))
    self.response.headers['Content-Type'] = "text/html"
    self.handle_commits(json_data)

  def convert_file(self, url, file_path):
    resp, content = self.http.request(url, "GET")
    markdown_html = self.markdowner.convert(content)
    s3_key = self.s3.new_key(re.sub(r"\.md$", ".html", file_path))
    s3_key.content_type = 'text/html'
    s3_key.set_contents_from_string(markdown_html)
    s3_key.make_public()
    self.response.write('written to s3?')

  def handle_added(self, git_commit):
    # todo
    return True

  def handle_removed(self, git_commit):
    # todo
    return True

  def handle_modified(self, git_commit):
    modified_files = git_commit['modified']
    url = git_commit['url']
    for modified_file in modified_files:
      modified_url = url.replace('commit', 'raw') + "/" + modified_file
      self.convert_file(modified_url, modified_file)
    

  def handle_commit(self, git_commit):
    self.handle_added(git_commit) 
    self.handle_removed(git_commit)
    self.handle_modified(git_commit)
    
  def handle_commits(self, git_post):
    [self.handle_commit(git_commit) for git_commit in git_post['commits']]
    

application = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/commit', CommitHandler)
], debug=True)
