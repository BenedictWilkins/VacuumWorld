#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 23:16:51 2019

@author: ben
"""


from .vwc import location, dirt, agent, coord
from collections import defaultdict
from inspect import signature
#import numpy as np

#--------------------------------------------------------

AGENT_COLOURS = set(['user', 'orange', 'green', 'white'])
DIRT_COLOURS = set(['orange', 'green'])

class VacuumWorldInternalError(Exception):
    pass
    
def __validate_agent(agent, colour):
    agent_dir = set(dir(agent))
    
    if not 'do' in agent_dir:
        print('ERROR:' + colour + ' agent must define the do method')
        return False
    else:
        if not callable(agent.do):
            print('ERROR:' + colour + 'agent do must be callable')
            return False
        else:
            if len(signature(agent.do).parameters) != 0:
                print('ERROR:' + colour + ': agent do must be defined with no arguments, do(self) or do()')
                return False
        
    if not 'revise' in agent_dir:
        print('ERROR:' + colour + ' agent must define the revise method')
        return False
    else:
        if not callable(agent.revise):
            print('ERROR:' + colour + ' agent revise must be callable')
            return False
        else:
             if len(signature(agent.revise).parameters) != 2:
                print('ERROR:' + colour + ' agent revise must be defined with two arguments, revise(self, observation, messages) or revise(observation, messages)')
                return False
        
    if not 'speak' in agent_dir:
        print('ERROR:' + colour + ':agent must define the speak method')
        return False
    else:
        if not callable(agent.speak):
            print('ERROR:' + colour + ' agent speak must be callable')
            return False
        else:
             if len(signature(agent.speak).parameters) != 0:
                print('ERROR:' + colour + ' agent speak must be defined with no arguments, speak(self) or speak()')
                return False
    return True

#change the name to grid if you want!
class Grid:
    DIRECTIONS = {'north':(0,-1), 'south':(0,1), 'west':(-1,0), 'east':(1,0)}
    
    ID_PREFIX_DIRT = 'D-'
    ID_PREFIX_AGENT = 'A-'
    
    GRID_MIN_SIZE = 3
    GRID_MAX_SIZE = 13
    
    def __init__(self, dim):
       self.reset(dim)
       self.agent_count = 0
       self.dirt_count = 0 
       self.cycle = 0
       
    def replace_all(self, grid):
        self.state = grid.state
        self.agent_count = grid.agent_count
        self.dirt_count = grid.dirt_count
        self.cycle = grid.cycle
       
    def reset(self, dim):
        self.cycle = 0
        self.state = {}
        for i in range(dim):
            for j in range(dim):
                self.state[coord(j,i)] = location(coord(j,i), None, None)
            self.state[coord(-1, i)] = None
            self.state[coord(i, -1)] = None
            self.state[coord(dim, i)] = None
            self.state[coord(i, dim)] = None
        self.state[coord(-1,-1)] = None
        self.state[coord(-1, dim)] = None
        self.state[coord(dim,-1)] = None
        self.state[coord(dim, dim)] = None
        self.dim = dim
        self.agent_count = 0
        self.dirt_count = 0
        
    def _in_bounds(self, coordinate):
        return coordinate.x >= 0 and coordinate.x < self.dim and coordinate.y >= 0 and coordinate.y < self.dim
    
    def _as_coord(self, coordinate):
        if not isinstance(coordinate, coord):
            return coord(coordinate[0], coordinate[1])
        return coordinate
    
    def dirt(self, colour):
        assert(colour in DIRT_COLOURS)
        self.dirt_count += 1
        return dirt(Grid.ID_PREFIX_DIRT + str(self.dirt_count), colour)
    
    def agent(self, colour, direction):
        assert(colour in AGENT_COLOURS)
        assert(direction in Grid.DIRECTIONS.keys())
        self.agent_count += 1
        return agent(Grid.ID_PREFIX_AGENT + str(self.agent_count), colour, direction)            
    
    def replace_agent(self, coordinate, agent):
         coordinate = self._as_coord(coordinate)
         assert(self._in_bounds(coordinate))
         loc = self.state[coordinate]
         self.state[coordinate] = location(coordinate, agent, loc.dirt)
         
    def replace_dirt(self, coordinate, dirt):
         coordinate = self._as_coord(coordinate)
         assert(self._in_bounds(coordinate))
         loc = self.state[coordinate]
         self.state[coordinate] = location(coordinate, loc.agent, dirt)
        
    def place_agent(self, coordinate, agent):
        coordinate = self._as_coord(coordinate)
        assert(self._in_bounds(coordinate))
        assert(self.state[coordinate].agent == None)
        loc = self.state[coordinate]
        self.state[coordinate] = location(coordinate, agent, loc.dirt)
        
    def place_dirt(self, coordinate, dirt):
        coordinate = self._as_coord(coordinate)
        assert(self._in_bounds(coordinate))
        assert(self.state[coordinate].dirt == None)
        loc = self.state[coordinate]
        self.state[coordinate] = location(coordinate, loc.agent, dirt)
    
    def remove_dirt(self, coordinate):
        assert(self._in_bounds(coordinate))
        loc = self.state[coordinate]
        self.state[coordinate] = location(coordinate, loc.agent, None)
        
    def remove_agent(self, coordinate):
        assert(self._in_bounds(coordinate))
        loc = self.state[coordinate]
        self.state[coordinate] = location(coordinate, None, loc.dirt)
        
    def move_agent(self, _from, _to):
        _from = self._as_coord(_from)
        _to = self._as_coord(_to)
        assert(self.state[_from].agent != None)
        assert(self.state[_to].agent == None)
        
        from_loc = self.state[_from]
        to_loc = self.state[_to]
        self.state[_to] = location(to_loc.coordinate, from_loc.agent, to_loc.dirt)
        self.state[_from] = location(from_loc.coordinate, None, from_loc.dirt)
        
    def turn_agent(self, _coordinate, orientation):
        assert(self.state[_coordinate].agent != None)
        loc = self.state[_coordinate]
        ag = loc.agent
        self.state[_coordinate] = location(_coordinate, agent(ag.name, ag.colour, orientation), loc.dirt)

