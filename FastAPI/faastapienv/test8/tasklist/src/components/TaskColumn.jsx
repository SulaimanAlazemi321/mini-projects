import React from "react";
import "./TaskColumn.css";
import Task from "./Task";

const icons = { "To Do":"🧾", Doing:"⏳", Done:"✔️" };

const TaskColumn = ({ status }) => (
  <section className="tc_scope">
    <div className="column">
      <div className="column_head">
        {status} <span className="status_icon">{icons[status] ?? "📦"}</span>
      </div>
      <div className="column_body">
        <Task task="cleaning" />
      </div>
    </div>
  </section>
);

export default TaskColumn;
