var url = document.location.href;
if (url.substring(0, 6) == "wtp://") {
	url = url.substring(6);
	// C'est une url pour le protocol, on fait une demande au serveur web local
	var request = new XMLHttpRequest();
	var commande = "=cmd rechercher nom "+encodeURIComponent(url.substring(6));
	var port = browser.runtime.connectNative("wtp_bridge");
	//Listen for messages from the app.
	port.onMessage.addListener((response) => {
		console.log("Received: " + response);
		port.disconnect();
	});
	port.postMessage(commande);
	alert("Sent : "+commande);
	if (result.substring(0, 15) == "=cmd SUCCESS : ") {
		alert("SHA : "+result.substring(16));
		document.location.href = result.substring(16);
	}
}

var links = document.getElementsByTagName("a");
var result = "";
for (var l = 0; l < links.length; l++){
	var lienActuel = links[l].href;
	if (lienActuel.substring(0, 6) == "wtp://") {
		// Maintenant on prépare l'envoi de la commande au serveur local
		alert("Attention !!")
		var request = new XMLHttpRequest();
		var commande = "=cmd rechercher nom "+encodeURIComponent(lienActuel.substring(6));
		var port = browser.runtime.connectNative("wtp_bridge");
		//Listen for messages from the app.
		port.onMessage.addListener((response) => {
			console.log("Received: " + response);
			port.disconnect();
		});
		port.postMessage(commande);
		alert("Sent : "+commande);
		if (result.substring(0, 15) == "=cmd SUCCESS : ") {
			alert("SHA : "+result.substring(16));
			document.getElementsByTagName("a")[0].href = result.substring(16);
		}
		else{
			alert(result);
		}
	}
}