import React from 'react'
import "./App.css"
import TaskForm from './components/TaskForm'
import Tag from './components/Tag'
import Task from './components/Task'
import TaskColumn from './components/TaskColumn'


const App = () => {
  return (
    <div>
      <TaskForm></TaskForm>
      <main className='app_main'>
        <TaskColumn status="To Do 📋"/>
        <TaskColumn status="Doing ⏳"/>
        <TaskColumn status="Done ✔️" />
   

    

      </main>
    </div>
  )
}

export default App