// Token template
const tokenSource = document.getElementById("token-template").innerHTML;
const tokenTemplate = Handlebars.compile(tokenSource);
const tokenPlaceholder = document.getElementById("tokens");

function refreshTokens() {
  const xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function () {
    if (this.readyState === 4 && this.status === 200) {
      const res_json = JSON.parse(this.responseText);
      tokenPlaceholder.innerHTML = tokenTemplate(res_json);
    }
  };
  xhttp.open("GET", "{{ url_for('refresh') }}", true);
  xhttp.send();
}

window.refreshTokens = refreshTokens;
