// import React from "react";
// import ReactDOM from "react-dom/client";
// import MainRouter from "./src/MainRouter";
// import "./src/index.css";

// const rootElement = document.getElementById("root");

// if (!rootElement) {
//   throw new Error("Could not find root element to mount to");
// }

// const root = ReactDOM.createRoot(rootElement);

// root.render(
//   <React.StrictMode>
//     <MainRouter />
//   </React.StrictMode>
// );


// import React from "react";
// import ReactDOM from "react-dom/client";
// import MainRouter from "./src/MainRouter";
// import "./src/index.css";

// const rootElement = document.getElementById("root");

// if (!rootElement) {
//   throw new Error("Could not find root element to mount to");
// }

// const root = ReactDOM.createRoot(rootElement);

// root.render(
//   <React.StrictMode>
//     <MainRouter />
//   </React.StrictMode>
// );



import React from "react";
import ReactDOM from "react-dom/client";
import MainRouter from "./src/MainRouter";
import LiquidEther from "./src/components/LiquidEther";

import "./src/index.css";
import "./App.css";

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    <div className="app-root">
      <div className="app-liquid-bg">
        <LiquidEther
          colors={["#5227FF", "#FF9FFC", "#B497CF"]}
          mouseForce={20}
          cursorSize={100}
          isViscous
          viscous={30}
          iterationsViscous={32}
          iterationsPoisson={32}
          resolution={0.5}
          isBounce={false}
          autoDemo
          autoSpeed={0.5}
          autoIntensity={2.2}
          takeoverDuration={0.25}
          autoResumeDelay={3000}
          autoRampDuration={0.6}
          color0="#5227FF"
          color1="#FF9FFC"
          color2="#B497CF"
        />
      </div>

      <div className="app-content">
        <MainRouter />
      </div>
    </div>
  </React.StrictMode>
);