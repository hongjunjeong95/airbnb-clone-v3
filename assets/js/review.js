import axios from "axios";

axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFToken";

const reviewAmends = document.querySelectorAll(".reviewAmend");
const reviewDelete = document.getElementById("reviewDelete");

const handleAmendInput = (event) => {
  event.preventDefault();
  const room_pk = window.location.href.split("/")[4];
  const form = event.target;
  const p = form.parentNode;
  const textarea = form.querySelector("textarea");
  const text = textarea.value;
  const review_pk = p.getAttribute("name");

  p.innerHTML = text;

  reviewAmends.forEach((reviewAmend) => {
    reviewAmend.addEventListener("click", handleAmend);
    reviewAmend.classList.remove("hidden");
  });

  axios({
    method: "POST",
    url: `/reviews/${room_pk}/${review_pk}/update/`,
    data: {
      review: text,
    },
  });
};

const handleAmend = (e) => {
  const btn = e.target;
  const btnParent = btn.parentNode.parentNode;
  const p = btnParent.nextSibling.nextSibling;
  const form = document.createElement("form");
  const textarea = document.createElement("textarea");
  const div = document.createElement("div");
  const submit = document.createElement("button");

  btn.removeEventListener("click", handleAmend);
  btn.classList.add("hidden");

  textarea.value = p.innerText;
  textarea.classList.add(
    "w-full",
    "h-20",
    "mb-2",
    "resize-none",
    "border",
    "border-black",
    "p-1",
    "rounded-lg"
  );
  p.innerText = "";

  div.classList.add("flex", "justify-end");

  submit.innerText = "Amend";
  submit.classList.add("review_button", "w-32", "bg-blue-600");

  div.append(submit);

  form.appendChild(textarea);
  form.appendChild(div);

  p.appendChild(form);
  p.childNode = form;

  form.addEventListener("submit", handleAmendInput);
};

const init = () => {
  if (reviewAmends) {
    reviewAmends.forEach((reviewAmend) => {
      reviewAmend.addEventListener("click", handleAmend);
    });
  }
};

init();
