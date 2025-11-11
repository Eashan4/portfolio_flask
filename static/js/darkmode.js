const btn = document.getElementById("theme-toggle");
if (localStorage.getItem("theme") === "dark") {
    document.body.classList.remove("light-theme");
    document.body.classList.add("dark-theme");
}
if (btn){
btn.addEventListener("click", () => {
    document.body.classList.toggle("dark-theme");
    if (document.body.classList.contains("dark-theme")) localStorage.setItem("theme", "dark");
    else localStorage.setItem("theme", "light");
});}
