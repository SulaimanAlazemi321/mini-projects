import React from 'react';
import './TaskForm.css';
import Tag from './Tag';
import {  LuChevronDown, LuShield, LuSparkles } from 'react-icons/lu';

const TaskForm = () => {
  return (
    <section className="tf_scope">
    <header className="app_header" role="banner" aria-label="Task Commander">
      {/* ambience layers */}
      <div className="header_glow" aria-hidden="true" />
      <div className="scanlines" aria-hidden="true" />

      <div className="header_inner">
        <div className="brand" aria-label="App brand">
          <LuShield className="brand_icon" />
          <span className="brand_text">
            Task<span>OS</span>
          </span>
          <LuSparkles className="brand_spark" aria-hidden="true" />
        </div>

        <form className="header_form" role="search" aria-label="Add task">
          <label htmlFor="taskInput" className="sr_only">Task Title</label>
          <input
            type="text"
            id="taskInput"
            className="input_text"
            placeholder="Type a task — e.g., “Implement auth middleware”"
          />

          <div className="form_tags_buttons">
            <div className="tags_row" aria-label="Tags (multi-select)">
              <Tag theTag="HTML" />
              <Tag theTag="CSS" />
              <Tag theTag="JavaScript" />
              <Tag theTag="React" />
            </div>

            <div className="controls_row">
              <div className="select_wrap">
                <label htmlFor="taskStatus" className="sr_only">Status</label>
                <select id="taskStatus" className="task_status" defaultValue="to-do">
                  <option value="to-do">To Do</option>
                  <option value="doing">Doing</option>
                  <option value="done">Done</option>
                </select>
                <LuChevronDown className="select_caret" aria-hidden="true" />
              </div>

              <button type="submit" className="task_submit">
                <span>Add Task</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </header>
    </section>

  );
};

export default TaskForm;
