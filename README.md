# Infection Algorithm

## Initial thoughts

Since the infection travels along both the "is coached by" and the "coaches" relationship, the total infection problem boils down to a determination of the connected components of an undirected graph where the nodes are the users and the edges are the coaching relations.

After writing the code to extract the connected components, I will use the counts of nodes in each of the connected components to implement the limited infection problem by finding a subset of the counts that adds up to approximately the desired number of infections. Depending on how close I would like to get to the target number, it could take a while for the subset selection.

Also, I need to figure out how I will partition the connected components if it turns out that too many users are grouped into large connected components. For example, if 1000 users are grouped into two components of sizes 400 and 600, but I only want to infect about 100 users, how will I decide how to break up. Maybe I'll approach the problem as a digraph problem, create a topological ordering, and then travel down the top-level coaching relationships until I find enough users. Or maybe I'll count the number of users under each coach and choose the single coach (along with descendents) who gets closest to the infection amount goal.

Also, I'm assuming 10 million users (somewhere on the internet it said that Khan Academy gets that many unique visitors each month). If the actual number is much larger, then my program might struggle to run in the memory of a single machine. In that case, I should possibly look at distributed algorithms for graph processing. In the past, I've read a little bit about processing graphs with hadoop. Something to look into.

Time to explore for a while...

## During the Process Thoughts

I just tried out the connected component algorithm on a file of 10 million users and the recursion limit for depth first search was reached. 

The change to breadth-first search seems to work much better. I was able to find an algorithm to search for a combination of connected components that adds up as close to a certain number as possible. Now I need to figure out how to split large components if necessary.

I just found a bug in the limited infection when it is run multiple times in a row. It generates a larger and larger group of users to process. The group contains duplicates which doesn't affect the final result, but causes extra processing. I'm almost done with my 12 hours, so I'll have to leave the bug in for now.

## Final Thoughts

Things to still address:

* The ability to break up large components into smaller ones if desired for partial infections
* The ability to process a graph that's too big to fit in memory
* More tests for the graph data structures and the infection functions
* More docstrings!

I'm also interested in a different way of approaching this problem by creating descendant counts for each coach and then being able to choose the infection population based on a coach's descendants. This will lead to problems when one student is coached by two different coaches, but it would lead to a more natural splitting of large components.