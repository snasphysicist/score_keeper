let vueApplication = new Vue({
  el: "#vue",
  data: {
    selectedstage: "",
    selectedgroup: "",
    selectedduel: "",
    selectedround: "",
    tournament: {},
    alldueldata: {},
    allduelrounds: []
  },
  computed: {
    allStages: function() {
      if (this.tournament["stages"]) {
        return tournament["stages"];
      } else {
        return [];
      }
    },
    stageGroups: function() {
      if (!this.tournament["stages"]) {
        return [];
      }
      // Filter down to selected stage
      let stage = this.tournament["stages"].filter(function(stage) {
        return stage["stage"]["number"] == this.selectedstage;
      })
      if (stage.length != 1) {
        return [];
      }
      return stage[0]["groups"];
    },
    groupDuels: function() {
      if (!this.tournament["stages"]) {
        return [];
      }
      // Filter down to selected stage
      let stage = this.tournament["stages"].filter(function(stage) {
        return stage["stage"]["number"] == this.selectedstage;
      })
      if (stage.length != 1) {
        return [];
      }
      let group = stage[0]["groups"].filter(function(group) {
        return group["group"]["number"] == this.selectedgroup;
      })
      if (group.length != 1) {
        return [];
      }
      return group[0]["duels"];
    },
    selectedRoundData: function() {
      let roundNumber = this.selectedround;
      for (let i = 0; i < this.allduelrounds.length; i++) {
        let nextRound = this.allduelrounds[i];
        if (nextRound["round_number"] == roundNumber) {
          return nextRound;
        }
      }
      return [];
    },
    formattedRoundScore: function() {
      if (this.selectedRoundData["score"]) {
        return this.selectedRoundData["score"]["opponent1"] + " : " + this.selectedRoundData["score"]["opponent2"];
      } else {
        return "---";
      }
    }
  }
});

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

function fetchDuelScores() {
  let dueltext = vueApplication.selectedduel;
  let options = document.getElementById("round-select").children;
  let duelId;
  for (let i = 0; i < options.length; i++) {
    if (options[i].innerHTML == dueltext) {
      duelId = options[i].getAttribute("duelid");
    }
  }
  const GET_URL = "/run_duel/api/v1/duel/<0>/score";
  // Insert ID into url
  let url = GET_URL.replace(
    "<0>",
    duelId
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
      vueApplication.alldueldata = json["duel"];
      vueApplication.allduelrounds = json["rounds"];
    } else {
      // Handle error
    }
  })
}

function getDuelsForGroup() {
  let groupId = vueApplication.selectedGroupId;
  console.log(groupId);
  // Exit if group id invalid
  if (groupId == null) {
    return;
  }
  const GET_URL = "/tournament/api/v1/<0>/overview";
  // Insert ID into url
  let url = GET_URL.replace(
    "<0>",
    groupId
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
    if (json["success"]) {
      vueApplication.duels = json["duels"];
      vueApplication.participants = json["participants"];
    }
  })
}

function doScoreAdjustment(event) {
  let clickedId = event.target.id;
  let whom;
  let action;
  if (clickedId.includes("1")) {
    opponent = 1;
  } else {
    opponent = 2;
  }
  if (clickedId.includes("up")) {
    action = "UP";
  } else {
    action = "DOWN";
  }
  let duelId = vueApplication.alldueldata["duel_id"];
  let roundId = vueApplication.selectedRoundData["round_id"];
  const POST_URL = "/run_duel/api/v1/duel/adjust";
  data = {
    duelid: duelId,
    action: action,
    opponent: opponent,
    roundid: roundId,
  }
  fetch(
    POST_URL,
    {
      method: "POST",
      body: JSON.stringify(data)
    }
  ).then((response) => {
    if (response.ok) {
      return response.json();
    }
  }).then((json) => {
    if (json["success"]) {
      fetchDuelScores();
    }
  })
}
