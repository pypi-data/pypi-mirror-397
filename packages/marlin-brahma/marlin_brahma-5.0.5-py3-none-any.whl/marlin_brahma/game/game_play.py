

import json, requests, random
from datetime import datetime, timedelta, timezone
from tqdm import tqdm as tq
import os, sys, random, pkgutil, math
from rich.progress import Progress
from loguru import logger as logger_
import pickle


import matplotlib.pyplot as plt

import matplotlib
import matplotlib.patches as mpatches
from matplotlib import colormaps
cmap = matplotlib.cm.get_cmap('Spectral')

from custom_decisions import *
from custom_transcription import *

import marlin_brahma.world.population as pop
import marlin_brahma.fitness.performance as performance
from marlin_brahma.evo.brahma_evo import *


#----------------------------------------------------------------------------
#                           IDENT GAME                                    #
#----------------------------------------------------------------------------




class GameMetrics(object):
    """GameMetrics | Handles all metrics for game and evolutionary performance. Simple returns for plotting functionality.

    :param object: _description_
    :type object: _type_
    """
    def __init__(self, game_id = "", dump_path = "", label_data =[]):
        
        self.game_id = game_id
        # generation data
        self.by_generation = []
        
        self.energy_tracker = {}
        # optimisation overview -> first view of framework running
        self.overview = {}
        # list of all saved bots (with gen number)
        self.saved_bots = []
        # p/l for all bots when saved
        self.results = {}
        
        self.dump_path = dump_path
        
        self.label_data = label_data
        
    def update_overview(self, overview = {}):
        self.overview = overview
    
    
        
    

    
    def update_saved_bots(self, bot_list=[], results={}):
        
        
        for bot_id in bot_list:
            bot_root = '_'.join(bot_id.split('_')[:-1])
            self.saved_bots.append(bot_id)
            self.results[bot_id] = results[bot_root]
        
        
    def update_gen(self, data = {}):
       
        gen_number = data['generation_number']
        tmp_results = {}
        for bot_id, result in data['results'].items():
            bot_id_ = f'{bot_id}_{gen_number}'
            tmp_results[bot_id_] = result
        
        data['results'] = tmp_results
        data['update_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['ss_ids'] = data['ss_ids']
        self.by_generation.append(data)
    
    def update_energy(self, tag, generation, data):
        if tag not in self.energy_tracker:
            self.energy_tracker[tag] = {}
        if generation not in self.energy_tracker[tag]:
            self.energy_tracker[tag][generation] = []
        
        self.energy_tracker[tag][generation].append(data)
    
    def dump(self, winners=[], generation = 0):
        
        self.by_generation[generation]['overview'] = {
            'saved_bots' : self.saved_bots,
            'results' : self.results
        }
        
        # overview data
        self.by_generation[generation]['parms'] = self.overview
        
        with open(f'{self.dump_path}/learn_out/gen_data_{self.game_id}.json', 'w') as fp:
            json.dump(self.by_generation,fp)
    
        with open(f'{self.dump_path}/energies/energy_data_{self.game_id}.json', 'w') as fp:
            json.dump(self.energy_tracker,fp)
        
    
    
    def build_output(self, data = None,sample_rate = 1, results = {},  labels = [],ss_id = 0, generation = 0, energy_data = {}, start_time=0, end_time=0):
        """
        Generate analysis data for generation, e.g. spectrogram and energies of interest
        """
        
        print (start_time, end_time)
        start_time_ms = datetime.datetime.strptime(start_time, '%y%m%d_%H%M%S.%f').replace(tzinfo=timezone.utc).timestamp() * 1000
        end_time_ms = datetime.datetime.strptime(end_time, '%y%m%d_%H%M%S.%f').replace(tzinfo=timezone.utc).timestamp() * 1000
        
        
        # Build and save spectrogram and energies of interest
        fig, ax1 = plt.subplots(figsize=(8, 8))
    
        # Spectrogram
        n_fft = 8192
        sample_rate = sample_rate
        plt.specgram(data, NFFT=n_fft, Fs=sample_rate, scale="dB",
                    mode="magnitude", cmap="ocean")
        plt.colorbar()
        
        # save
        filepath = f'{self.dump_path}/analysis/{self.game_id}_{generation}T{ss_id}.png'
        plt.legend(handles=labels)
        plt.ylabel('Frequency (Hz)')
        plt.xlabel('Time (s)')
        plt.savefig(filepath)
        plt.clf()
        
        
        
        
        # Energies and labels
        label_y = 0.5
        label_pts = []
        # print (self.label_data)
        # exit()
        for k,label in self.label_data.items():
            # print (label)
            start_t = label[0]
            end_t = label[0]
            mid = (float(start_t) + float(end_t))/2
            
            # print (mid, start_time_ms,end_time_ms)
            if (float(start_t)> float(start_time_ms)) and (float(start_t) < float(end_time_ms)):
                pts = [float(start_t),float(end_t)]
                start_dt = datetime.datetime.fromtimestamp((float(start_t)/1000),timezone.utc)
                end_dt = datetime.datetime.fromtimestamp((float(end_t)/1000),timezone.utc)
                start_str = start_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                end_str = end_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                label_pts.append([start_str, end_str])
            
            
        
        # plot labels
        fig, ax1 = plt.subplots(figsize=(8, 8))
        rgba = cmap(random.random())
        for label in label_pts:
            
            time_from = datetime.datetime.strptime(label[0],"%Y-%m-%dT%H:%M:%S.%fZ")
            time_to = datetime.datetime.strptime(label[1],"%Y-%m-%dT%H:%M:%S.%fZ")
            print (time_from,time_to)
            plt.plot([time_from,time_to],[0.9,0.9],color="green", marker="o" )
            # plt.scatter(time_from, 1.0,color="green", marker="o" )
            
           
        # add energy profiles of interesting bots
        for bot_id, value in results.items():
            # grab data
            
            if bot_id not in energy_data:
                continue
            energy_data = energy_data[bot_id]
            
            # build energy profile for bot
            e_values = []
            t_values = []
            
            for entry in energy_data:
                e_value = float(entry[0])
                time_str = entry[2]
                
                iter_time = datetime.datetime.strptime(time_str,"%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                
                iter_ms = iter_time.timestamp() * 1000
                if iter_ms >= start_time_ms and iter_ms < end_time_ms:
                    e_values.append(e_value)
                    t_values.append(iter_time)
            
            # plot profile
            plt.plot(t_values, e_values,color="blue")
            
        
        # save
        filepath = f'{self.dump_path}/analysis/{self.game_id}_{generation}T{ss_id}_energy.png'
        plt.legend(handles=labels)
        plt.ylabel('Frequency (Hz)')
        plt.xlabel('Time (s)')
        plt.savefig(filepath)
        plt.clf()
            
        
    
class IdentGame(object):
    """IdentGame _summary_

    :param object: _description_
    :type object: _type_
    """
    def __init__(self, population = None,performance = None,data_feed = None, derived_data = None, multiple_derived_data = {},game_id = "", game_parms = {}, label_data=[], dmdb_flag = False, init_expression_load = False, dump_path="", bot_path=""):
        """__init__ _summary_

        :param data_manager: _description_, defaults to None
        :type data_manager: _type_, optional
        :param game_id: _description_, defaults to ""
        :type game_id: str, optional
        :param game_parms: _description_, defaults to {}
        :type game_parms: dict, optional
        :param label_data: _description_, defaults to []
        :type label_data: list, optional
        """
        
         # ---- DUMP PATHS ---
        self.dump_path = dump_path
        if self.dump_path == "":
            return None
        
        self.bot_path = bot_path
        if self.bot_path == "":
            return None
        if game_id == "":
            self.game_id =str(math.floor(random.random()*99999999))
        else:
            self.game_id = game_id
        self.metrics = GameMetrics(self.game_id, dump_path, label_data = label_data)
        
        self.population = population
        self.performance = performance
        self.myTournament = None
        
        
        self.energy_tracker = {}
        self.data_feed = data_feed
        self.derived_data = derived_data 
        self.multiple_derived_data = multiple_derived_data
        self.game_id = game_id
        self.bulk_energies = {}
        self.bulk_times = {}
        self.game_parms = game_parms
        self.activation_level = game_parms['activation_level']
        self.live_decisions = 0
        self.number_decisions = 0
        
        # --- Data structures for recording decision analysis,data and energies -> for those bots saved ---
        self.decision_raw_data_recorder = {}
        self.bot_decision_tracker = {}
        self.bot_energy_tracker = {}
        
        self.story = {}
        self.label_data = label_data
        
        # --- Reporting JSON ---
        self.static_rpt = {}
        self.dynamic_rpt = {}
        
        # --- Optimisation
        self.hit_idx = {}
        self.op_run = False
        
        # --- DMDB implementation
        self.dmdb_flag = dmdb_flag
        self.dmdb_expression = {}
        self.init_expression_load = init_expression_load
        
       # --- Trackers for analysis
        self.bot_energy_tracker = {}
        
        
    def generation_reset(self):
        # print ("reseting generation data")
        self.performance = None
        self.performance = performance.Performance()
        
        # print ("reseting generation data...done")
        
    def update_dmdb_expression(self,generation_number=0):
        """initialise_dmdb | Initialise output data of dmdb. 
        Loop over DMs in DMDB and build expression structure.
        """
        
        if self.init_expression_load:
            with open('dm/expression_dm.exp', 'rb') as fp:
                self.dmdb_expression = pickle.load(fp)
                tag = list(self.dmdb_expression.keys())[0]
                d = len(self.dmdb_expression[tag])
                
                print (f"length : {d}")
                
                # for tag, data in self.dmdb_expression.items():
                #     print (len(data))
                
                # print (self.dmdb_expression)
                
                return (1)
        
        # --- Iterate over DMDB
        _population_size_ = len(list(self.population.dmdb.keys()))
        _cnt_ = 0
        for dm_id, dm in self.population.dmdb.items():
            _cnt_ += 1
            if dm_id not in self.dmdb_expression:
                self.dmdb_expression[dm_id] = []
            if len(self.dmdb_expression[dm_id])<1:
                # we have a new dm
                
                logger_.info(f"Updating expression vector for {dm_id} | {_cnt_} of {_population_size_}")
                self.bot_step(dm,dmdb_express_update=True,dm_id = dm_id)
                
        with open('dm/expression_dm.exp', 'wb') as fp:
                pickle.dump(self.dmdb_expression,fp)
        
        return (1)
    
    def play(self):
        """ play | play runs the Ident game main iteration loop. The function iterated
        """
        game_initialised = False
        generation_number = 0
        self.update_dmdb_expression(generation_number = generation_number)
        logger_.trace(self.dmdb_expression)
        
        self.metrics.update_overview(self.game_parms)
                
        
        with Progress() as progress:
            
        # --- Iterate over generations
            for op_run in range(1,self.game_parms['number_generations']):
                # update task bar
                task1 = progress.add_task("[red]Running features (bots)...", total=len(self.population.bots))
                
                # reset generation fitness structure
                self.generation_reset()
                
                # --- Iterate over individuals
                for individual_idx in range(0, len(self.population.bots)):
                    # get bot name and run bot life
                    bot_name = self.population.bots[individual_idx]
                    self.bot_step(self.population.species[bot_name], generation=generation_number)
                    progress.update(task1, advance=1)
                    print (f'{bot_name}')
                
                # --- All individuals have been run -> now evaluate them all
                self.performance.evaluateBots(self.population.species,self.game_parms)
                best_fitness, worst_fitness, winner_id, fitness_data = self.performance.text_output_fitness()
                logger_.info(f'<=== Generation {generation_number} | best [{best_fitness}] | worst [{worst_fitness}] | winning bot [{winner_id}] ===>')
                
                

                # --- We have all the fitness values now, time to *** EVOLVE ***
                saved_ids = self.evolve(generation=generation_number)
                
                
                
                
                
                # --- Build output analysis for energies ---
                ss_ids = []
                for env_pressure in self.data_feed:
                    waveform = env_pressure.frequency_ts_np
                    print (env_pressure.meta_data)
                    sr = env_pressure.meta_data['sample_rate']
                    self.metrics.build_output( data = waveform,sample_rate = sr, results = self.myTournament.results, labels=[], ss_id = env_pressure.meta_data['snapshot_id'],generation = generation_number, energy_data = self.bot_energy_tracker, start_time=env_pressure.meta_data['data_frame_start'], end_time=env_pressure.meta_data['data_frame_end'] )
                    ss_ids.append(env_pressure.meta_data['snapshot_id'])
                
                decision_text = self.performance.showBotDecisions(bot_name=winner_id, verbose=False)
                self.metrics.update_saved_bots(bot_list = saved_ids, results=self.myTournament.results)
                self.metrics.update_gen({'generation_number' : generation_number, 'best' : best_fitness, 'worst' : worst_fitness, 'winner':winner_id, 'decisions': decision_text, 'saved_bots' : saved_ids, 'results' : self.myTournament.results, 'ss_ids' : ss_ids })
                self.metrics.dump(winners=self.myTournament.winners, generation = generation_number)
                
                
                generation_number += 1    
                
                
                
    def add_decision(self,listen_start_idx, iter_cnt, bot, iter_start_time, iter_end_time, pressure_id, sr):
        """transcribe _summary_

        :param iter_cnt: _description_
        :type iter_cnt: _type_
        :param bot: _description_
        :type bot: _type_
        :param iter_start_time: _description_
        :type iter_start_time: _type_
        :param iter_end_time: _description_
        :type iter_end_time: _type_
        :param pressure_id: _description_
        :type pressure_id: _type_
        """
        # self.number_decisions += 1
        
        decision_id = 'd_id_' + str(math.floor(random.uniform(0,999999))) + str(math.floor(random.uniform(0,999999))) + str(math.floor(random.uniform(0,999999)))
        # print ("decision made")
        max_memory = bot.GetMemory()
        xr_start_time = iter_start_time - timedelta(milliseconds=max_memory)
        
        decision_args = {
            'status' : 1,
            'memory' : max_memory,
            'env' : self.game_parms['env'],
            'xr_start' : xr_start_time,
            'iter_start_time' : iter_start_time,
            'iter_end_time' : iter_end_time,
            'action' : 1,
            'type' : "IDent",
            'xr' : -1,
            'epoch' : pressure_id,
            'decision_id' : decision_id,
            'iter_cnt' : iter_cnt
        }
        
        new_decision = IdentDecision(decision_data=decision_args)
        self.performance.add_decision(decision=new_decision, epoch = pressure_id, botID = bot.name)
        
        
        # ================================================
        # query dataset to mark decision
        # ================================================
        
        # print (iter_end_time)
        xr_hits = self.derived_data.query_label_time(xr_start_time, iter_end_time)
        # print (xr_start_time)
        # print(xr_hits)
        if len(xr_hits) == 0:
            print (xr_start_time, iter_end_time)
            exit()
        # exit()
        # if len(xr_hits)==0:
        #     xr_hits = self.query_label_time(xr_start_time, iter_end_time)

        if len(xr_hits) > 0:
            
            self.live_decisions += 1
            xr_data = xr_hits[0]
            if xr_data['xr'] == True:
                xr = True
                
        else:
            xr = False
        
        # ================================================

        
        decision_args = {
            'status' : 0,
            'memory' : max_memory,
            'xr_start' : xr_start_time,
            'env' : self.game_parms['env'],
            'iter_start_time' : iter_start_time,
            'iter_end_time' : iter_end_time,
            'action' : 0,
            'type' : "IDent",
            'xr' : xr,
            'epoch' : pressure_id,
            'decision_id' : decision_id,
            'iter_cnt' : iter_cnt
        }


        # i_s_i = listen_start_idx - (math.floor(1 * sr))
        # interesting_slice_idx = max(0,(i_s_i))
        # decision_show_data = env_pressure.frequency_ts_np[interesting_slice_idx:slice_end]
        
        # self.decision_raw_data_recorder[decision_id] = decision_show_data
        # if bot.name in self.bot_decision_tracker:
        #     self.bot_decision_tracker[bot.name].append(decision_id)
        # else:
        #     self.bot_decision_tracker[bot.name] = []
        #     self.bot_decision_tracker[bot.name].append(decision_id)
        # record
        close_decision = IdentDecision(decision_data=decision_args)                    
        self.performance.add_decision(decision=close_decision, epoch = pressure_id, botID = bot.name)
    
    def bot_step(self, bot = None, generation=0, dmdb_express_update = False, dm_id=0):
        """bot_step | A single iteration of a bot in the population domain. It iterates over all environment pressures provided to the 
        game.

        :param bot: _description_, defaults to None
        :type bot: _type_, optional
        :param generation: _description_, defaults to 0
        :type generation: int, optional
        """
        
        # full life iter counter
        total_iter_cnt = 0
        # full life time counter
        global_time_counter = 0
        # global time recroder
        global_time_recorder = []
        
        # optimsation mode [not currently active]
        op = False
        interesting_start = 0
        
        
        # trackers for analysis
        self.bot_energy_tracker[bot.name] = []
        
        # --- Iterate over environment pressures (data snapshot downloaded from data repo)
        for env_pressure in self.data_feed:
            
            # get snapshot id
            pressure_id = env_pressure.meta_data['snapshot_id']
            sr = env_pressure.meta_data['sample_rate']
            # reset counters
            listen_start_idx = 0
            listen_end_idx = 0
            # step size for given delta t of game
            listen_delta_idx = math.floor(self.game_parms['listen_delta_t'] * env_pressure.meta_data['sample_rate'])
            # get total indices in the data vector
            env_pressure_length = env_pressure.frequency_ts_np.shape[0]
            
            # local inter counter
            iter_cnt = 0
            
            # iterate over data vector
            while listen_start_idx < (env_pressure_length - (listen_delta_idx*2)):
                
                # --- START PRE LOGIC HOUSEKEEPING ---
                
                # get start & end slice idx ---
                listen_end_idx = listen_start_idx + listen_delta_idx
                slice_start = listen_start_idx
                slice_end = min(listen_end_idx,env_pressure_length-1)
                
                # get seconds of iter start from start of dataset
                _s = (slice_start / env_pressure.meta_data['sample_rate']) * 1000 # ms 
                # get iteration start time in standard format
                iter_start_time =  env_pressure.start_time + timedelta(milliseconds=_s)
                curr_date_string = iter_start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                
                # get seconds of iter end from start of dataset
                _s = (slice_end / env_pressure.meta_data['sample_rate']) * 1000
                iter_end_time   =  env_pressure.start_time  + timedelta(milliseconds=_s)
                logger_.trace(f'{iter_start_time} -> {iter_end_time}')
                # logger_.info(f'{global_time_counter} | {iter_end_time}')
                # print ((f'{global_time_counter} | {iter_end_time}'))
                # --- END PRE LOGIC HOUSEKEEPING ---
                
                
                # --- START GAME LOGIC ---
                
                
                
                data = {'target' : "" ,'dmdb_data':self.population.dmdb, 'dmdb_expression_vector' : self.dmdb_expression, 'generation': generation, 'op':op,'bot_id': bot.name,'sim_delta_t':self.game_parms['listen_delta_t'],'global_iter_count':total_iter_cnt ,'timings' : self.game_parms['timings'],'data_index':listen_start_idx - interesting_start, 'sample_rate' : env_pressure.meta_data['sample_rate'] ,'current_data' :  env_pressure.frequency_ts_np.shape[slice_start:slice_end], 'derived_model_data' : self.multiple_derived_data[pressure_id], 'iter_start_time' : iter_start_time, 'iter_end_time' : iter_end_time ,'nirvana':self.label_data}
                
                logger_.trace(bot)
                if dmdb_express_update:
                    # update the expression structure for dmdb
                    gene_value = bot.run(data,dmdb_flag = False)
                    # get expression level
                    self.dmdb_expression[dm_id].append(gene_value)
                else:
                    # run genetic expression
                    ex_stat = bot.ExpressDNA(data,dmdb_flag = self.dmdb_flag)
                    # get expression level
                    express_level = bot.GetAvgExpressionValue()
                    # print (express_level)
                    
                    # self.metrics.update_energy(bot.name, generation, energy_data)
                    
                    # get transcription data
                    transcription_data = {
                            'expression_data': bot.GetExpressionData(),
                        }
                    
                    protein_present = bot.transcriptionDNA.run_transcription(bot, dmdb_structure=self.population.dmdb, dmdb_expression_vector=self.dmdb_expression,global_iter_count=total_iter_cnt,transcription_data=transcription_data, dmdb_flag = True)
                    
                    if protein_present:
                        self.add_decision(listen_start_idx,iter_cnt, bot, iter_start_time, iter_end_time, pressure_id, sr)
                        express_level = 0.9
                        
                        
                    
                    # save energy level for analysis
                    if bot.name not in self.bot_energy_tracker:
                        self.bot_energy_tracker[bot.name] = []
                        # print (global_time_counter)
                        self.bot_energy_tracker[bot.name].append([express_level,global_time_counter,curr_date_string])
                    
                    else:
                        # print (global_time_counter)
                        self.bot_energy_tracker[bot.name].append([express_level,global_time_counter,curr_date_string])
                        
                    
                    # update energy tracker
                    energy_data = {'energy' : express_level, 'time' : curr_date_string}


                # --- END GAME LOGIC ---
                
                
                
                # --- START UPDATE COUNTERS ---
                iter_cnt += 1
                total_iter_cnt += 1
                # print (f'total_iter_cnt : {total_iter_cnt}')
                listen_start_idx = listen_end_idx
                global_time_counter = self.game_parms['listen_delta_t'] + global_time_counter
                global_time_recorder.append(global_time_counter)
                # --- END UPDATE COUNTERS ---

    def evolve(self, generation = 0):
    
        """

        Evolution Step 1.
        =============================================
        All the bots have now been evaluated. The bots now compete in a tournament and are ranked. 
        Once ranked, the bot population is regernated. There are a number of ways of doing this. BrahmA
        root structures provide a quick development environment for getting the AI engine off the ground.
        BrahmA provides more sophisticated algorithms and custom algos can also be used. Be sure
        to derive your class definitions from the correct root structures.

        We will use a simple tournament/rank and regeneration algorithm.


        Step 1. Create the Tournament structure and compete.

        """ 
        self.myTournament = None
        self.myTournament = SimpleTournamentRegenerate(generationEval = self.performance.evaluation, population = self.population, dataManager = None)

        """

        Step 2. Tournament Rank

        """
        
        winners = self.myTournament.RankPopulation()
        # print (self.myTournament.results)
        self.myTournament.printRankings()
        
        """

        Step 3. Regenerate Population
        Here bots are killed, children are created and the population of bots is 
        regenerated.

        """

        self.myTournament.RegeneratePopulation(dmdb_flag = self.dmdb_flag)
        
        """
        Step 4. The Genetic Shuffle
        Mutation plays a very significant role in evolution by altering gene points within the 
        genome.
        """

        genetic_shuffle = RootMutate(population = self.population, config = self.game_parms )
        genetic_shuffle.mutate(args=self.game_parms, dmdb_flag = self.dmdb_flag)
        
                
        #---generate list of zeros
        
        zeros = self.myTournament.Zeros()
        
        
        #---kill list of zeros
        self.population.KillDeadWood(tags = zeros) 
        #--------------------------------

        #---regenerate population
        self.population.Repopulate(species=self.population.species_name) 
        #--------------------------------
        
    
        # --- Save winning bots ---
        saved_ids = self.population.DMDB_saveBots(self.myTournament.winners, data={'generation' : generation, 'bot_path':self.bot_path})    
        
        return saved_ids
        


