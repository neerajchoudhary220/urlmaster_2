const base_url = "http://127.0.0.1:8090";
const open_parent_dir = $("#open-parent-dir");
const getHerdLink = (selector) => {
  return selector.data("herd_link");
};
const reloadWindow = () => {
  window.location.reload();
};
function getRequest({
  url,
  onSuccess = () => {},
  onError = (errorMsg) => showHackerAlert(errorMsg),
  onComplete = () => {},
  showLoader = true,
}) {
  $.ajax({
    method: "GET",
    url: url,
    beforeSend: function () {
      if (showLoader) showLoading();
    },
    success: function (res) {
      onSuccess(res);
    },
    error: function (xhr) {
      let errorMsg = "An error occurred";
      if (xhr.responseJSON && xhr.responseJSON.detail) {
        errorMsg = xhr.responseJSON.detail;
      }
      onError(errorMsg);
    },
    complete: function () {
      if (showLoader) hideLoading();
      onComplete();
    },
  });
}

function showLoading() {
  document.getElementById("hacker-loader").classList.remove("d-none");
}

function hideLoading() {
  document.getElementById("hacker-loader").classList.add("d-none");
}

function showHackerAlert(message = "Something happened!", callback = () => {}) {
  const alertBox = document.getElementById("hacker-alert");
  const messageBox = document.getElementById("hacker-alert-message");
  const okButton = document.getElementById("hacker-alert-ok");

  messageBox.textContent = message;
  alertBox.classList.remove("d-none");

  const handleClick = () => {
    hideHackerAlert();
    callback();
    okButton.removeEventListener("click", handleClick); // Clean up
  };

  okButton.addEventListener("click", handleClick);
}

function hideHackerAlert() {
  document.getElementById("hacker-alert").classList.add("d-none");
}

const copyLink = (contents) => {
  // Create a temporary input element
  var $temp = $("<input>");
  $("body").append($temp);
  $temp.val(`${contents}`).select();
  document.execCommand("copy");
  $temp.remove();
  showHackerAlert("Copied Successfully!");
};

//Fetch List
function fetchList() {
  getRequest({
    url: `${base_url}/directory/`,
    onSuccess: function (res) {
      const directories = res.data.directories;
      const tbody = $("#directory-table tbody");
      tbody.empty();

      directories.forEach((dir, index) => {
        open_parent_dir
          .attr("data-dir_path", dir.parent_dir)
          .text(dir.parent_dir_name);
        const active_branch = `<span>${dir.active_branch}</span>`;
        const directory = `<div class="d-flex justify-content-start"><div class="me-auto"><span style="cursor:pointer;" class="text-cyan open-directory ellipsis" data-dir_path="${dir.path}">${dir.name}</span> <i class="fa fa-folder-open text-cyan"></i></div> </div>`;
        const clone_directory_btn = `<button class="btn btn-info text-cyan clone-directory-btn ms-2" data-dir_path="${dir.path}"><i class="fa fa-window-restore text-cyan"></i></button>`;
        const herd_link = dir.herd_link
          ? `<div class="d-flex justify-content-start"><a href="${dir.herd_link}" target="_blank" class="me-auto ellipsis text-cyan">${dir.herd_link}</a> <button class="btn btn-sm btn-secondary copy-herd-link-btn"><i class="fa fa-clone"></i></button></div>`
          : `<button class="btn btn-primary text-cyan add-with-herd-btn" data-path="${dir.path}">Add Herd Link</button>`;
        let generate_url = "";

        if (dir.public_url) {
          generate_url = `<div class="d-flex justify-content-start"><a href="${dir.public_url}" target="_blank" class="me-auto ellipsis text-cyan">${dir.public_url}</a> <button class="btn btn-sm btn-secondary copy-public-url-btn"><i class="fa fa-clone"></i></button></div>`;
        } else if (dir.herd_link) {
          generate_url = `
    <div class="btn-group">
      <button class="btn btn-sm btn-outline-primary genereate-public-url-btn" data-dir-path="${dir.path}" data-herd_link="${dir.herd_link}">
        Generate Public URL
      </button>
    </div>`;
        } else {
          generate_url = `
    <div class="alert alert-danger p-0 p-1 mt-3 w-75" role="alert">
      Herd link is not available!
    </div>`;
        }
        const regenerate_public_url = dir.public_url
          ? `<button class="btn btn-info text-cyan regenerate-public-url-btn" data-bs-toggle="popover" data-bs-trigger="hover" title="Regenerate Public URL" data-dir-path="${dir.path}" data-herd_link="${dir.herd_link}"><i class="fa fa-exchange"></i></button>`
          : " ";
        const delete_public_url = dir.public_url
          ? `<button class="btn btn-info ms-2 delete-url-btn text-cyan" data-herd_link="${dir.herd_link}"><i class="fa fa-ban text-cyan"></i></button>`
          : "";
        const row = `
                    <tr>
                        <th scope="row">${index + 1}</th>
                        <td>${directory}</td>
                        <td>${active_branch}</td>
                        <td>${herd_link}</td>
                        <td><div class="w-75">${generate_url}</div></td>
                        <td>
                          <div class='d-flex w-100'>${regenerate_public_url} ${delete_public_url} ${clone_directory_btn}</div>
                        </td>
                    </tr>
                `;

        tbody.append(row);
      });
    },
  });
}

//Generate Public URL
function generatePublicUrl(this_, herd_link) {
  getRequest({
    url: `${base_url}/cloudflared/?herd_link=${herd_link}&dir_path=${this_.attr(
      "data-dir-path"
    )}`,
    onSuccess: function (res) {
      showHackerAlert(res.msg);
    },
    onComplete: function () {
      reloadWindow();
    },
  });
}

$(document).ready(function () {
  fetchList(); //Fetch list data

  //click to Add Parent Directory Button
  $("#add_parent_directory_btn").on("click", function () {
    $(this).parent().addClass("d-none");
    $("#add_parent_directory_group").removeClass("d-none");
  });

  //Click To Close Parent Dir Btn
  $("#close-add-parent-dir").on("click", function () {
    $("#add_parent_directory_group").addClass("d-none");
    $("#add_parent_directory_btn").parent().removeClass("d-none");
  });

  //Add parent directory
  $("#add").on("click", function () {
    const data_ = {
      path: $("#parent_directory_path").val(),
    };
    $.ajax({
      url: `${base_url}/directory/`,
      method: "post",
      data: JSON.stringify(data_),
      contentType: "application/json",
      success: function (response) {
        // alert("Successfully saved");
        showHackerAlert("Successfully Saved!");
      },
      error: function (xhr) {
        if (xhr.responseJSON && xhr.responseJSON.detail) {
          const error_msg = xhr.responseJSON.detail;
          showHackerAlert(error_msg);
        } else {
        }
      },
    });
  });

  // Change branch event delegation
  // $(document).on("change", ".branch-dropdown", function (e) {
  //   const selectedBranch = $(this).val();
  //   const directoryPath = $(this).data("path");
  //   getRequest({
  //     url: `${base_url}/git/switch/?path=${directoryPath}&branch=${selectedBranch}`,
  //     onSuccess: function (res) {
  //       showHackerAlert(res.msg);
  //     },
  //     onComplete: function () {},
  //   });
  // });

  //Add with Herd
  $(document).on("click", ".add-with-herd-btn", function () {
    const dir_path = $(this).data("path");
    getRequest({
      url: `${base_url}/herd/?directory_path=${dir_path}`,
      onSuccess: function (res) {
        showHackerAlert(res.msg, function () {
          reloadWindow();
        });
      },
      onComplete: function () {
        // reloadWindow();
      },
    });
    // $.ajax({
    //   method: "get",
    //   url: `${base_url}/herd/?directory_path=${dir_path}`,

    //   success: function (response) {
    //     showHackerAlert(response.msg);
    //   },
    //   error: function (xhr) {
    //     if (xhr.responseJSON && xhr.responseJSON.detail) {
    //       const error_msg = xhr.responseJSON.detail;
    //       showHackerAlert(error_msg);
    //     }
    //   },
    //   complete: function () {
    //     window.location.reload();
    //   },
    // });
  });

  //Generate Public URL
  $(document).on("click", ".genereate-public-url-btn", function () {
    const this_ = $(this);
    generatePublicUrl(this_, getHerdLink(this_));
  });

  //Regenerate Public URL
  $(document).on("click", ".regenerate-public-url-btn", function () {
    const this_ = $(this);
    generatePublicUrl(this_, getHerdLink(this_));
  });

  //delete Public URL
  $(document).on("click", ".delete-url-btn", function () {
    const this_ = $(this);
    $.ajax({
      method: "DELETE",
      url: `${base_url}/cloudflared/?herd_link=${getHerdLink(this_)}`,
      beforeSend: function () {
        showLoading();
      },
      success: function (response) {
        alert(response.msg);
      },
      error: function (xhr) {
        if (xhr.responseJSON && xhr.responseJSON.detail) {
          const error_msg = xhr.responseJSON.detail;
          alert(error_msg);
        }
      },
      complete: function () {
        hideLoading();
        window.location.reload();
      },
    });
  });

  //clone directory
  $(document).on("click", ".clone-directory-btn", function () {
    const dir_path = $(this).data("dir_path");
    $("#dir_path").val(dir_path);
    $("#cloneDirectoryModal").modal("show");
  });

  $("#clone_dir_form").on("submit", function (e) {
    e.preventDefault(); // Prevent the default form submission
    let newDirName = $("#new_dir_name").val(); // Get input value
    const dir_path = $("#dir_path").val();

    $.ajax({
      method: "GET",
      url: `${base_url}/directory/clone/?directory_path=${dir_path}&new_folder_name=${newDirName}`,
      success: function (response) {
        alert(response.msg);
      },
      error: function (xhr) {
        if (xhr.responseJSON && xhr.responseJSON.detail) {
          const error_msg = xhr.responseJSON.detail;
          alert(error_msg);
        }
      },
      complete: function () {
        window.location.reload();
      },
    });
  });

  //Open Directory
  $(document).on("click", ".open-directory,#open-parent-dir", function () {
    const path = $(this).data("dir_path");
    $.ajax({
      method: "GET",
      url: `${base_url}/directory/open/?path=${path}`,
      success: function (response) {
        // alert(response.msg);
      },
      error: function (xhr) {
        if (xhr.responseJSON && xhr.responseJSON.detail) {
          const error_msg = xhr.responseJSON.detail;
          alert(error_msg);
        }
      },
      complete: function () {},
    });
  });

  $(document).on(
    "click",
    ".copy-herd-link-btn, .copy-public-url-btn",
    function () {
      copyLink($(this).parent().find("a").text());
    }
  );
});
