let vueApplication = new Vue({
  el: "#vue",
  data: {
    selectedstage: "",
    selectedgroup: "",
    selectedduel: "",
    selectedround: "",
    tournamentduels: [],
    alldueldata: {},
    allduelrounds: []
  },
  computed: {
    allStages: function() {
      let stages = [];
      for (let i = 0; i < this.tournamentduels.length; i++) {
        let duel = this.tournamentduels[i];
        let inArray = false;
        for (let j = 0; j < stages.length; j++) {
          if (stages[j]["id"] == duel["stageid"]) {
            inArray = true;
            break;
          }
        }
        if (!inArray) {
          stages.push(
            {
              "id": duel["stageid"],
              "number": duel["stagenumber"]
            }
          )
        }
      }
      return stages;
    },
    stageGroups: function() {
      // Get all groups for the selected stage
      let groups = [];
      let stagenumber = this.selectedstage;
      for (let i = 0; i < this.tournamentduels.length; i++) {
        let duel = this.tournamentduels[i];
        // Immediately stop if this duel is not even in the right stage
        if (duel["stagenumber"] != stagenumber) {
          continue;
        }
        let inArray = false;
        for (let j = 0; j < groups.length; j++) {
          if (groups[j]["id"] == duel["groupid"]) {
            inArray = true;
            break;
          }
        }
        if (!inArray) {
          groups.push(
            {
              "id": duel["groupid"],
              "number": duel["groupnumber"]
            }
          )
        }
      }
      return groups;
    },
    groupDuels: function() {
      let duels = [];
      let stagenumber = this.selectedstage;
      let groupnumber = this.selectedgroup;
      for (let i = 0; i < this.tournamentduels.length; i++) {
        let duel = this.tournamentduels[i];
        // Immediately stop if this duel is not even in the right stage
        if (duel["stagenumber"] != stagenumber) {
          continue;
        }
        // Stop this iteration if this duel is not in the right group
        if (duel["groupnumber"] != groupnumber) {
          continue;
        }
        // If we made it here, this duel is in the stage & group
        duels.push(duel);
      }
      return duels;
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
      vueApplication.tournamentduels = json["duels"];
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
