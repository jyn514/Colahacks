var branches = {};  // dictionary of string branch name to GitGraph branch
var commits = {};   // dictionary of string commit name to {branch: name of branch, pos: integer distance from first commit}
var latest = "";    // sha1 hash for latest commit
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
  var scrollbar = document.getElementById("gitGraph_scrollbar");
  var scroll_width = scrollbar.offsetWidth;
  var canvas_width = document.getElementById("gitGraph").offsetWidth;
  var commit_pos = commit_width * commits[commit].pos - scroll_width / 2;
  if (commit_pos < 0) commit_pos = 0;
  if (commit_pos >= canvas_width - scroll_width) commit_pos = canvas_width - scroll_width;
  scrollbar.scrollLeft = commit_pos;
}


// Adds a commit to the gitGraph object\
function git_commit(branch, current, parent, msg, link, type="none", merge_parent="") {
  // TODO(HD) these autofill cases should be removed before the final product

  if (!parent) {
    // Fill in parent with latest commit if not specified
    parent = latest;
  }

  if (!branch) {
    // Fill in branch with parent's if not specified
    branch = commits[parent].branch
  }

  // If parent and branch are both specified and don't line up, that could
  //   cause problems, but everything should be specified from the back end

  if (!(branch in branches)) {
    // TODO(HD) actually
    if (!parent || !(parent in commits)) {
      branches[branch] = gitGraph.branch(branch);
    } else {
      branches[branch] = branches[commits[parent].branch].branch(branch);
    }
  }

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

  if (merge_parent) {
    // Do a merge from merge_parent branch into branches[branch]
    merge_branch = branches[commits[merge_parent].branch];
    merge_branch.merge(branches[branch], commit_info);
  } else {
    // Else do a regular commit
    branches[branch].commit(commit_info);
  }

  var commit_pos = 0;  // Pos is zero if latest is not in commits (i.e. this is first commit)
  if (latest in commits) {
    commit_pos = commits[latest].pos;
    if (parent in commits && commits[latest].branch == commits[parent].branch
        || (merge_parent in commits && commits[latest].branch == commits[merge_parent].branch)) {
      commit_pos += 1;
    }
  }

  commits[current] = {branch: branch, pos: commit_pos};

  latest = current;
}
