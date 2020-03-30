
var vueApplication = new Vue({
  el: '#vue',
  data: {
    tournament: {
      stages: []
    }
  }
});

function deleteDuel(event) {
  let duelId = event.target.getAttribute("duelid");
  let data = {
    "duelid": duelId
  };
  const DELETE_URL = "/run_duel/api/v1/duel/delete";
  fetch(
    DELETE_URL,
    {
      method: "DELETE",
      body: JSON.stringify(data)
    }
  ).then((response) => {
    if (response.ok) {
      return response.json();
    }
  }).then((json) => {
    if(json["success"]) {
      // Re-fetch duel list
      fetchDuelList();
    } else {
      // Handle error
    }
  })
}

function fetchDuelList() {
  const TOURNAMENT_ID = 3;
  const GET_URL = "/run_duel/api/v1/<0>/duel/list";
  // Insert ID into url
  let url = GET_URL.replace(
    "<0>",
    TOURNAMENT_ID
  );
  fetch(
    url,
    {
      method: "GET",
    }
  ).then((response) => {
    if (response.ok) {
      return response.json();
    }
  }).then((json) => {
    if(json["success"]) {
      vueApplication.tournament = json["tournament"];
    } else {
      // Handle error
    }
  })
}

fetchDuelList();
