---
hide:
  - navigation
  - toc
---
<style>
  .md-main__inner {
    margin-top: 0;
  }
@media screen and (min-width: 76.1875em) {
  .md-sidebar {
    display: none;
  }
  #pip-button {
    width: 20em;
    font-size: 1.1rem;
    float: left;
    cursor: pointer;
  }
  #get-started-button {
    font-size: 1.1rem;
    width: 20em;
    cursor: pointer;
  }
}
@media screen and (max-width: 76.1875em) {
  #pip-button {
    font-size: 1.0rem;
    width: 20em;
    cursor: pointer;
  }
  #get-started-button {
    font-size: 1.0rem;
    width: 20em;
    cursor: pointer;
    margin-bottom: 20px;
  }
}
  .test {
    align: center;
  }

.center {
    text-align: center;
  }

h1 {
  display: none;
}

</style>
<script type="text/javascript">
  function copy_install_text(btn){
    var inp = document.createElement('input');
    document.body.appendChild(inp);
    inp.value = "pip install meerschaum";
    inp.select();
    document.execCommand('copy',false);
    inp.remove();
    old_btn_text = btn.text;
    btn.text = "Copied!";
    window.setTimeout(() => {
      btn.text = old_btn_text;
    }, 2000);
    return false;
   }
</script>

<link rel="stylesheet" type="text/css" href="/assets/css/asciinema-player.css" />
<link rel="stylesheet" type="text/css" href="/assets/css/grid.css" />
<script src="/assets/js/asciinema-player.js"></script>

<!-- <script src="https://platform.linkedin.com/badges/js/profile.js" async defer type="text/javascript"></script> -->
![Meerschaum Banner](banner_1920x320.png)

<!-- # Welcome to the Meerschaum Documentation Home Page -->

<!-- If you'd like to incorporate Meerschaum into your project, head over to [docs.meerschaum.io](https://docs.meerschaum.io) for technical API documentation of the `meerschaum` package. -->

<p style="text-align:center; color:#666666; font-size: 1.2em"><i>Out-of-the-box ETL, easy to learn, and a pleasure to use!</i></p>

<div class="grid-container center">
  <div class="grid-child">
    <a id="get-started-button" class="md-button md-button--primary" href="get-started">Get Started</a>
  </div>
  <div class="grid-child" >
    <a id="pip-button" class="md-button" href="#!" style="font-family: monospace" onclick="copy_install_text(this)">$ pip install meerschaum<span class="twemoji">
</a>
  </div>
</div>

<div class="grid-container">
  <div class="grid-child">
    <h2>What is Meerschaum?</h2>
    <p>Meerschaum is a platform for quickly creating and managing time-series data streams called <b><a href="/reference/pipes/">pipes</a></b>. With Meerschaum, you can have a data visualization stack running in minutes.</p>
    <h2>Why Meerschaum?</h2>
    <p>If you've worked with time-series data, you know the headaches that come with ETL. Meerschaum is a system that makes consolidating and syncing data easy.</p>
    <p>Meerschaum instead gives you better tools to define and sync your data streams. And don't worry — you can always incorporate Meerschaum into your existing scripts.</p>

  </div>
  <div class="grid-child">
    <br>
    <asciinema-player src="/assets/casts/demo.cast" autoplay="true" loop="true" size="small" preload="true"></asciinema-player>
  </div>
</div>

<h2> Video Tutorials</h2>

<div class="grid-container">
  <div class="grid-child">

  <div style="text-align: center">
    <iframe width="672" height="378" src="https://www.youtube.com/embed/t9tFD4afSD4" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
  </div>


  </div>
  <div class="grid-child">

  <div style="text-align: center">
    <iframe width="672" height="378" src="https://www.youtube.com/embed/iOhPn4RjImQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
  </div>

  </div>
</div>

<div class="grid-container">
  <div class="grid-child">
  <h2>Support the Project</h2>
    <p style="text-align: left">I work on Meerschaum in my free time, so if you enjoy the project and want to support its development, feel free to <a href="https://www.buymeacoffee.com/bmeares">buy me a coffee</a>! You can also support the project on my <a href="https://github.com/sponsors/bmeares">GitHub Sponsors page</a>.
    </p>
    <div class="center">
      <!-- <script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="bmeares" data-color="#5F7FFF" data-emoji="🍺"  data-font="Cookie" data-text="Buy me a beer" data-outline-color="#000000" data-font-color="#ffffff" data-coffee-color="#FFDD00" ></script> -->
    </div>
  </div>
  <div class="grid-child">
    <h2>Consulting Services</h2>
    <p>If you're looking to recruit my skills, you can hire my consulting services. Reach out on <a href="https://linkedin.com/in/bennettmeares">LinkedIn</a> to get in touch, or you can commission my help at my <a href="https://github.com/sponsors/bmeares">GitHub Sponsors page</a>.</p>
  </div>
</div>
