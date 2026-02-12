# cpf-concours

Spec:

* Know about available rooms in each period. Ideally, know about room capacity.
* Know about each school's judges and participants.
* For each participant, know about their category.
* Know about category lengths.
* Know about our student volunteers.
* Propose room assignments such that each room has, at a minimum,
  * 1 volunteer
  * 2 judges
  * 1 category
* Room requirement: no judge with any student of their own school.
* Room optimization: judges from different schools.
* Room optimization: balance category lengths.
* Room optimization: judges and volunteers stay in the same place across periods.
 
Algorithm:

1. For each RoomSchedule (RS), keep a pool of eligible judges and eligible categories (i.e., that do not conflict with existing ones).
2. For each judge and category, keep a pool of eligible RSes.
3. Place a random category or judge on a random eligible RS. [Perhaps the one with the least time so far.]
4. Update the eligibility lists.
5. Repeat the last two steps, branching recursively. Whenever it becomes impossible to place a given category or judge (i.e. they have no eligibility left), abandon the branch.
6. If all are placed, submit that branch.

Can be improved by replacing "random" with "optimal" (e.g., by sorting so as to keep similar categories together, judges with the same room across periods, judges from the same school not together).
