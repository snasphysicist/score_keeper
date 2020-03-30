  var vueApplication = new Vue({
    el: '#vue',
    data: {
      currentstage: 0,
      groups: [],
      participants: [],
      allduels: [],
      stageformat: ""
    }
  })

/*
 * Patterns used in round robin duel generation
 * Explicitly written out since I have not
 * yet found an algorithm that can avoid producing
 * series of duels where someone has to duel
 * multiple times in a row too often
 */
const DUEL_PATTERNS = {
  2: [
    [0, 1]
  ],
  3: [
    [0, 1],
    [0, 2],
    [1, 2]
  ],
  4: [
    [0, 1],
    [2, 3],
    [0, 2],
    [1, 3],
    [3, 0],
    [1, 2]
  ],
  5: [
    [0, 1],
    [2, 3],
    [4, 0],
    [1, 2],
    [3, 4],
    [0, 2],
    [1, 3],
    [2, 4],
    [3, 0],
    [4, 1]
  ],
  6: [
    [0, 1],
    [2, 3],
    [4, 5],
    [3, 0],
    [4, 1],
    [5, 2],
    [0, 4],
    [1, 2],
    [3, 5],
    [0, 2],
    [1, 5],
    [3, 4],
    [5, 0],
    [1, 3],
    [2, 4]
  ]
}

let selected = null;
function toggleGroupSelect(event) {
    // Update selected group
    selected = event.target;
    // Update display to reflect this
    // First clear any selected buttons
    let currently_selected = document.querySelectorAll(".selected");
    currently_selected.forEach(function(button) {
      button.classList.remove("selected");
    })
    // Now display clicked one as selected
    selected.classList.add("selected");
}

function assignParticipant(event) {
    // Get participant id from button
    let participantId = event.target.getAttribute("participantid");
    let battleName = event.target.id;
    // Do nothing if no group selected
    if (!selected) {
        return;
    }
    // Assume group already exists
    let groupId = selected.getAttribute("groupid");
    let group = findGroupById(groupId);
    group["members"].push(
      {
        participantid: participantId,
        battlename: battleName
      }
    );
    hideParticipants();
}

function findGroupById(groupId) {
  let group = vueApplication.groups.filter(function(group) {
    return group["id"] == groupId;
  });
  if (group.length === 1) {
    return group[0];
  } else {
    return null;
  }
}

function unassignParticipant(event) {
    let participantId = event.target.getAttribute("participantid");
    let groups = vueApplication.groups.filter(function(group) {
      // Find members in group with correct participant id
      let member = group["members"].filter(function(member) {
        return member["participantid"] == participantId;
      });
      // Keep if this participant appears in members array
      return (member.length > 0);
    })
    // For each group that contains this participant
    groups.forEach(function(group) {
      // Get the participant object in the group
      let toRemove = group["members"].filter(function(member) {
        return member["participantid"] == participantId;
      });
      if (toRemove.length != 1) {
        return;
      }
      /*
       * Remove the element at this participants' index
       * (i.e. this participant)
       */
      group["members"].splice(
        group["members"].indexOf(
          toRemove[0]
        ),
        1
      );
    });
    // Update which participants are shown/hidden
    hideParticipants();
}

function hideParticipants() {
    // First get all assigned participants
    let assigned = [];
    // We'll also check if everyone has already been assigned
    let allAssigned = true;
    vueApplication.groups.forEach(function(group) {
      group["members"].forEach(function(member) {
        assigned.push(
          member["participantid"];
        );
      });
    });
    // Now get all participant inputs
    let participantSection = document.getElementById("all-participants");
    let participantInputs = participantSection.children;
    participantInputs.forEach(function(button) {
      if (
          assigned.indexOf(
              button.getAttribute("participantid")
          ) > -1
      ) {
          // Disable when assigned
          button.disabled = true;
      } else {
          // Enable when unassigned
          button.disabled = false;
          allAssigned = false;
      }
    /*
     * Generate should be clickable
     * if all fighters assigned
     * AND duels not yet generated
     */
    let generateButton = document.getElementById("generate");
    if(allAssigned && vueApplication.allduels.length == 0) {
      generateButton.disabled = false;
    } else {
      generateButton.disabled = true;
    }
}

function generateDuels() {
  // DISABLE ONLY ON SUCCESS
  let didGenerate = false;
  if (vueApplication.currentStage["format"] == "ROUND-ROBIN") {
    didGenerate = generateRoundRobinDuels();
  } else if (vueApplication.currentStage["format"] == "CROSS-ROUND-ROBIN") {
    didGenerate = generateCrossRoundRobinDuels();
  }
  if (didGenerate) {
    // Disable generate button
    let generateButton = document.getElementById("generate");
    generateButton.disabled = true;
    // Enable confirm button
    let confirmButton = document.getElementById("confirm");
    confirmButton.disabled = false;
  }
}

/*
 * Functions for different
 * stage format duel
 * combination algorithms
 */
// Simple round robin

function generateRoundRobinDuels() {
  // Generate duels for each group
  let maxDuels = 0;
  for (let i = 0; i < vueApplication.groups.length; i++) {
    // Shuffle members
    let group = vueApplication.groups[i];
    let members = group["members"];
    members = shuffle(members);
    // Get combinations for this number of duellists
    let combinations = DUEL_PATTERNS[members.length];
    // Set up duels with those combinations
    for (let j = 0; j < combinations.length; j++) {
      let duel = {
        group: group["id"],
        opponent1: members[combinations[j][0]],
        opponent2: members[combinations[j][1]]
      };
      group.duels.push(duel);
    }
    if (group.duels.length > maxDuels) {
      maxDuels = group.duels.length;
    }
  }
  // Display on screen
  for (let i = 0; i < maxDuels; i++) {
    for (let j = 0; j < vueApplication.groups.length; j++) {
      if (i < vueApplication.groups[j]["duels"].length) {
        vueApplication.allduels.push(
          vueApplication.groups[j]["duels"][i]
        )
      }
    }
  }
  return true;
}

// Cross round robin
function generateCrossRoundRobinDuels() {
  // Only works with even number of groups
  if (vueApplication.groups.length % 2 != 0) {
    return false;
  }
  // For each pair of groups
  let i = 0;
  while (i < vueApplication.groups.length) {
    let group1 = vueApplication.groups[i];
    let group2 = vueApplication.groups[i + 1];
    let groupPairs = twoGroupsCrossRoundRobinDuels(
      group1,
      group2
    )
    for (let j = 0; j < groupPairs.length; j++) {
      let duel = {
        group: group1["id"],
        opponent1: groupPairs[j][0],
        opponent2: groupPairs[j][1]
      };
      vueApplication.allduels.push(
        duel
      );
    }
    // Next pair
    i = i + 2;
  }
  return true;
}

/* Different cases for cross round robin
 * Returns an array of pairs for duel
 */
function twoGroupsCrossRoundRobinDuels(
  group1,
  group2
) {
  let totalDuels = group1.members.length * group2.members.length;
  let pairs = [];
  let offset = 0;
  // Create arrays that pair participants
  for (let i = 0; i < totalDuels ; i++) {
    let nextPair = [];
    nextPair.push(
      group1.members[i % group1.members.length]
    );
    nextPair.push(
      group2.members[(i + offset) % group2.members.length]
    );
    // Check if pair already added
    if (pairAlreadyAdded(pairs, nextPair)) {
      /*
       * Shift one of the arrays by one
       * to generate new pairs next time
       */
      offset++;
      /*
       * Since the current iteration won't
       * get added, do it again on the
       * next loop iteration
       */
      i--;
    } else {
      pairs.push(nextPair);
    }
  }
  return pairs;
}

function pairAlreadyAdded(
  pairs,
  nextPair
) {
  for (let i = 0; i < pairs.length; i++) {
    let aPair = pairs[i];
    if (
      aPair[0]["participantid"] == nextPair[0]["participantid"]
      && aPair[1]["participantid"] == nextPair[1]["participantid"]
    ) {
      return true;
    }
  }
  return false;
}

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
      let j = Math.floor(Math.random() * (i + 1));
      let x = array[i];
      array[i] = array[j];
      array[j] = x;
  }
  return array;
}

// Get initial details - groups, participants, etc...
function getSetupDetails() {
  const GET_URL = "/tournament/api/v1/setup_duels";
  fetch(
    GET_URL,
    {
      method: "GET",
    }
  ).then((response) => {
    if (response.ok) {
      return response.json();
    }
  }).then((json) => {
    if (json["success"]) {
      vueApplication.currentStage = json["currentstage"];
      vueApplication.groups = json["groups"];
      vueApplication.participants = json["participants"];
    }
  })
}

getSetupDetails();

// Confirm duels, create in database
function confirmDuels() {
  let confirmButton = document.getElementById("confirm");
  confirmButton.disabled = true;
  let data = vueApplication.allduels;
  const POST_URL = "/tournament/api/v1/confirm_duels";
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
    if(json["success"]) {
      // Redirect to new duel page
    } else {
      // Re-enable button
      confirmButton.disabled = false;
    }
  })
}
