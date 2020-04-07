let vueApplication = new Vue({
  el: "#vue",
  data: {
    selectedstage: "",
    selectedgroup: "",
    selectedduel: "",
    tournament: {
      stages: []
    }
  },
  computed: {
    allStages: function() {
      if (this.tournament["stages"]) {
        return this.tournament["stages"];
      } else {
        return [];
      }
    },
    stageGroups: function() {
      // Get all groups for the selected stage
      if (!this.pendingduels["stages"]) {
        console.log("1");
        return [];
      }
      let stage = this.pendingduels["stages"].filter(function(stage) {
        return stage["stage"]["number"] == this.selectedstage;
      });
      if (stage.length == 0) {
        console.log("2");
        return [];
      }
      console.log("3");
      return stage[0]["groups"];
    },
    groupDuels: function() {
      if (!this.pendingduels["stages"]) {
        return [];
      }
      /*
       * Filter down to selected stage
       * Map to extract groups
       * Will then have array in array [[group1, group2, ...]]
       * So extract first element
       */
      let groups = this.pendingduels["stages"].filter(function(stage) {
        return stage["stage"]["number"] == this.selectedstage;
      }).map(function(stage) {
        return stage["groups"];
      })[0];
      if (!groups) {
        return [];
      }
      // Filter down to selected group
      let group = groups.filter(function(group) {
        return group["group"]["number"] == this.selectedgroup;
      })
      if (group.length == 0) {
        return [];
      }
      return group[0]["duels"];
    }
  }
});

/*
 * When fetching a list of pending
 * duels, suggest which should be next
 */
function setSuggestedNextDuel() {
  if (!vueApplication.pendingduels["stages"]) {
    return;
  }
  // Get stages/groups with duels
  let pendingStages = vueApplication.pendingduels["stages"].filter(function(stage) {
    let groups = stage["groups"].filter(function(group) {
      return group["duels"].length > 0;
    })
    return groups.length > 0;
  });
  if (pendingStages[0]) {
    let suggestedStage = pendingStages[0];
    let suggestedGroup = pendingStages[0]["groups"][0];
    let suggestedDuel = pendingStages[0]["groups"][0]["duels"][0];
    vueApplication.selectedstage = suggestedStage["stage"]["number"];
    vueApplication.selectedgroup = suggestedGroup["group"]["number"];
    vueApplication.selectedduel = suggestedDuel["opponent1"] + " vs "
      + suggestedDuel["opponent2"];
  }
}

// Fetch all pending duel details from api
function fetchPendingDuels() {
  const GET_URL = "/run_duel/api/v1/pending_duels";
  fetch(
    GET_URL,
    {
      method: "GET"
    }
  ).then((response) => {
    if(response.ok) {
      return response.json();
    } else {
      // Handle error
    }
  }).then((json) => {
    if (json["success"]) {
      vueApplication.pendingduels = json["pending"];
      if (json["pending"].length > 0) {
        setTimeout(setSuggestedNextDuel, 100);
      }
    }
  });
}

function startNewDuel() {
  const POST_URL = "/run_duel/api/v1/new_duel";
  // Need to find id of selected duel
  // Get all elements with duelid attribute
  let duels = document.querySelectorAll("option[duelid]");
  // Find inner html that matches selection
  let duelid;
  for (let i = 0; i < duels.length; i++) {
    let duel = duels[i];
    if (duel.innerText == vueApplication.selectedduel) {
      duelid = duel.getAttribute("duelid");
      break;
    }
  }
  let data = {
    "id": duelid
  };
  fetch(
    POST_URL,
    {
      method: "POST",
      body: JSON.stringify(data)
    }
  ).then((response) => {
      if(response.ok) {
        window.location.href = "/run_duel/current"
      } else {
        // Handle error
      }
  })
}

fetchPendingDuels();
setSuggestedNextDuel();
