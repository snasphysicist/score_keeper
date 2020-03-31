
var vueApplication = new Vue({
  el: '#vue',
  data: {
    duels: []
  }
});

function resetDuel(event) {
  let duelId = event.target.getAttribute("duelid");
  let data = {
    "duelid": duelId
  };
  const PATCH_URL = "/run_duel/api/v1/duel/reset";
  fetch(
    PATCH_URL,
    {
      method: "PATCH",
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
      vueApplication.duels = json["duels"];
    } else {
      // Handle error
    }
  })
}

fetchDuelList();
