import random
import numpy as np

class EightQueens:
    def __init__(self, table_size = 8, pop_size = 100, cross_rate = 0.9, mut_rate = 0.4, max_par = 5):
        self.table_size = table_size
        self.pop_size = pop_size
        self.cross_rate = cross_rate
        self.mut_rate = mut_rate
        self.max_par = 5
    
    def population_gen(self):
        pop = []
        
        for i in range(self.pop_size):
            seq = []
            while len(seq)<self.table_size: #checa se um numero foi adicionado
                pos_nn = random.randint(1, self.table_size) #possivel novo numero
                if pos_nn not in seq:
                    seq.append(pos_nn)
                    
            pop.append(seq)
            
        return pop
    
    def fitness(self, ind): #inverso da penalidade
        encounters = 0
        
        for i in range(self.table_size):
            for j in range(self.table_size):
                if i == j:
                    continue
                else:
                    if ind[i] == ind[j]:
                        encounters+=1
                    if abs(ind[i] - ind[j]) == abs(i-j):
                        encounters+=1
                

        penalty = encounters/2 #a penalidade vai ser o número de encontros entre rainhas possíveis
        fit = 1/(1+penalty) #quando a penalidade for 0, teremos o fitness de 100%
        
        return fit     
    
    ## TORNEIO

    def select_par(self, pop):
        possible_parents = [random.randint(0, self.pop_size-1) for i in range(self.max_par)]
        
        par_fitness = []
        for p in possible_parents:
            par_fitness.append(self.fitness(pop[p]))
            
        
        par1 = possible_parents[np.argsort(par_fitness)[-1]] #best parent 1
        par2 = possible_parents[np.argsort(par_fitness)[-2]] #best parent 2
        
        return par1, par2

    def select_par_rd(self, pop):
        par_fitness = []
        for p in pop:
            par_fitness.append(self.fitness(p))
            
        par1 = random.choices(list(range(len(pop))), par_fitness)
        
        par2 = random.choices(list(range(len(pop))), par_fitness)
        while par2 == par1:
            par2 = random.choices(list(range(len(pop))), par_fitness)
        
        return par1[0], par2[0]

    def cross_aux(self, par1, par2, cross_point):
        used = [False]*(self.table_size+1)
        
        child1 = []
        for i in range(0, cross_point):
            child1.append(par1[i])
            
            used[par1[i]] = True
        
        
        
        j = 0
        for i in range(cross_point, self.table_size):
            while(used[par2[j]] == True):
                j+=1
            child1.append(par2[j])
            used[par2[j]] = True
        
        return child1

    def new_cut_crossfill(self, parents, population):
        cross_point = random.randint(1, self.table_size-1)
        par1, par2 = population[parents[0]], population[parents[1]]
        
        child1 = self.cross_aux(par1, par2, cross_point)
        child2 = self.cross_aux(par2, par1, cross_point)
        
        return child1, child2
    
    def mutate(self, offsprings):
    
        for child in offsprings:
            x = 0
            y = 0
            while x == y:
                x = random.randint(0, self.table_size-1)
                y = random.randint(0, self.table_size-1)
            
            aux = child[x]
            child[x] = child[y]
            child[y] = aux

        return offsprings
    
    def new_pop(self, pop, children):
        pop_fitness = []
        
        for p in range(self.pop_size):
            fit = self.fitness(pop[p])
            pop_fitness.append((p, fit))
        
        pop_sorted = sorted(pop_fitness, key=lambda x: x[1])
        
        subs = (pop_sorted[0][0], pop_sorted[1][0])
        
        
        pop[subs[0]] = children[0]
        pop[subs[1]] = children[1]
        
        return  pop
    
    def execute(self, max_tests, see_converge = False, all_converge = False):
        tests = 0
        generation = 0 
        pop = self.population_gen()
        sol = False

        avg_fit = []
        inds_converged = 0
        
        all_done = False
        if all_converge == False:
            while tests < max_tests and sol == False:
                test_fitness = 0
                for ind in pop:
                    test_fitness += self.fitness(ind)
                    
                    if self.fitness(ind) == 1: #não há colisões
                        sol = True
                        inds_converged+=1
                    
                    tests+=1

                avg_fit.append(test_fitness/self.pop_size)
                if sol == False:
                    generation+=1
                
                    #print("solução não encontrada. fitness médio: " + str(test_fitness/self.pop_size) + ". geracao: " + str(generation))
                    
                    if random.random() < self.cross_rate: 
                        parents = self.select_par_rd(pop)
                        
                        offsprings = self.new_cut_crossfill(parents, pop)
                        if random.random() < self.mut_rate:
                            new_gen = self.mutate(offsprings)

                            pop = self.new_pop(pop, new_gen)
                        else:
                            pop = self.new_pop(pop, offsprings)

        else:
            while inds_converged < self.pop_size:
                test_fitness = 0
                inds_converged = 0
                for ind in pop:
                    test_fitness += self.fitness(ind)
                    
                    if self.fitness(ind) == 1: #não há colisões
                        sol = True
                        inds_converged+=1
                    
                    tests+=1

                avg_fit.append(test_fitness/self.pop_size)
                
                generation+=1
            
                #print("solução não encontrada. fitness médio: " + str(test_fitness/self.pop_size) + ". geracao: " + str(generation))
                
                if random.random() < self.cross_rate: 
                    parents = self.select_par(pop)
                    offsprings = self.new_cut_crossfill(parents, pop)
                    if random.random() < self.mut_rate:
                        new_gen = self.mutate(offsprings)

                        pop = self.new_pop(pop, new_gen)
                    else:
                        pop = self.new_pop(pop, offsprings)
            
        last_it = generation
        mean_fit = np.mean(avg_fit)
        converged = sol
        if see_converge==False:
            return converged, last_it, mean_fit, inds_converged
        else:
            return converged, avg_fit