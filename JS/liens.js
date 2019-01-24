var links = document.getElementsByTagName("a");
var result = "";
for (var l = 0; l < links.length; l++){
	var lienActuel = links[l].href;
	if (lienActuel.substring(0, 6) == "wtp://") {
		// Maintenant on prépare l'envoi de la commande au serveur local
		var request = new XMLHttpRequest();
		var commande = "=cmd%20rechercher%20nom%20"+encodeURIComponent(lienActuel.substring(6));
		request.open('GET', 'http://localhost:8888/'+commande);
		request.responseType = 'text';
		request.onload = function() {
			result = request.response;
			if (result.substring(0, 15) == "=cmd SUCCESS : ") {
				alert("SHA : "+result.substring(16));
				document.getElementsByTagName("a")[0].href = result.substring(16);
			}
		};
		request.send();
	}
}
