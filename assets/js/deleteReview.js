import axios from "axios";

axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFToken";

const reviewDeletes = document.querySelectorAll(".reviewDelete");

const handleDelete = (e) => {
  const btn = e.target;
  const reviewNode = btn.parentNode.parentNode.parentNode;
  const reviewSection = reviewNode.parentNode;
  const review_pk = reviewNode.id;
  const room_pk = window.location.href.split("/")[4];

  reviewSection.removeChild(reviewNode);

  axios({
    method: "POST",
    url: `/reviews/${room_pk}/${review_pk}/delete/`,
  });
};

const init = () => {
  if (reviewDeletes) {
    reviewDeletes.forEach((reviewDelete) => {
      reviewDelete.addEventListener("click", handleDelete);
    });
  }
};

init();
