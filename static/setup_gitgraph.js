var branches = {};  // dictionary of string branch name to GitGraph branch
var commits = {};   // dictionary of string commit name to {branch: name of branch, pos: integer distance from first commit}
var latest = "";
var commit_spacing = 20;
var commit_dotsize = 6;
var commit_width = commit_spacing;  // TODO(HD) figure out why it doesn't exactly line up

// GitGraph object will be modified later
var gitGraph = new GitGraph({
  orientation: "horizontal-reverse",
  mode: "compact",
  template: new GitGraph.Template({
    commit: {
      dot: {
        size: commit_dotsize
      },
      spacingY: commit_spacing,
      tooltipHTMLFormatter: function (commit) {
        return "" + commit.sha1.substring(0, 6) + ": " + commit.message + " (" + commit.branch.name + ")";
      }
    }
  })
});


// Calculates the position of a commit and scrolls 'gitGraph_scrollbar' to view it
function scroll_to(commit) {
  // TODO(HD) remove debugging print statements
  console.log("scrolling to " + commit);
  var scrollbar = document.getElementById("gitGraph_scrollbar");
  var scroll_width = scrollbar.offsetWidth;
  var canvas_width = document.getElementById("gitGraph").offsetWidth;
  var commit_pos = commit_width * commits[commit].pos - scroll_width / 2;
  console.log("scroll_width: " + scroll_width);
  console.log("canvas_width: " + canvas_width);
  console.log("commits[commit].pos: " + commits[commit].pos);
  console.log("commit_pos: " + commit_pos);
  if (commit_pos < 0) commit_pos = 0;
  if (commit_pos >= canvas_width - scroll_width) commit_pos = canvas_width - scroll_width;
  console.log("~commit_pos: " + commit_pos);
  scrollbar.scrollLeft = commit_pos;
}


// Adds a commit to the gitGraph object
function git_commit(branch, current, parent, msg, link, type="none") {
  if (!parent) {
    parent = latest;
  }

  if (!(branch in branches)) {
    // TODO(HD) actually
    if (!parent || !(parent in commits)) {
      branches[branch] = gitGraph.branch(branch);
    } else {
      branches[branch] = branches[commits[parent].branch].branch(branch);
    }
  }

  var commit_pos = (parent in commits) ? commits[parent].pos + 1 : 0;

  commits[current] = {branch: branch, pos: commit_pos};

  var commit_info = {
    sha1: current,
    message: msg,
    onClick: function(commit) {
      window.location.href=link;
    }
  };

  if (type == "current") {
    commit_info.dotColor = "red";
  }

  branches[branch].commit(commit_info);
  latest = current;
}
