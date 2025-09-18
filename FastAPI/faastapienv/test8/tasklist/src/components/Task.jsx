import React from "react";
import "./Task.css";

const Task = ({ task }) => {
  return (
    <div className="task_scope">
      <article className="task_card">
        <header className="task_header">
          <h4 className="task_title">{task}</h4>
          <button className="DeleteButton" aria-label="Delete task" />
        </header>

        <div className="tags">
          <span className="tag_chip">HTML</span>
          <span className="tag_chip">JavaScript</span>
        </div>
      </article>
    </div>
  );
};

export default Task;
