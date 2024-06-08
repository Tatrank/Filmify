function deleteFilm(film_id) {
  console.log(film_id);
  fetch(`/delete/${film_id}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then(() => {
      window.location.reload();
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}
