"""Example how to use the relaxed serialization"""
import pytodotxt

todotxt = pytodotxt.TodoTxt("todo.txt",
                            serializer=pytodotxt.serialize_relaxed)
todotxt.parse()

# Completed task with a completion date, but without creation date
# would lose the completion date with the default (pedantic) serializer
new_task = pytodotxt.Task("x 2010-01-01 Prepare new year")
todotxt.add(new_task)

todotxt.save()