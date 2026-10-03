import React from "react";
import {createRoot} from "react-dom/client";
import Portfolio from "@/components/portfolio";
import Studio from "@/components/studio";
import "@/styles/site.css";
function App(){
  const [studio,setStudio]=React.useState(window.location.hash.startsWith("#/studio"));
  React.useEffect(()=>{const change=()=>{setStudio(window.location.hash.startsWith("#/studio"));};window.addEventListener("hashchange",change);return()=>window.removeEventListener("hashchange",change);},[]);
  return studio?<Studio/>:<Portfolio/>;
}
createRoot(document.getElementById("root")!).render(<React.StrictMode><App/></React.StrictMode>);
