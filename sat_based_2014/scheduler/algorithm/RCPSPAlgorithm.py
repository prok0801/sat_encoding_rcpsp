import time

try:
    import psutil, os
except ImportError:
    psutil = None

from pysat.solvers import Glucose3  # Using Glucose3 instead of Minisat22

# Import the project’s modules.
from ..encoding.SATEncoder import SATEncoder
from ..encoding.SATDecoder import SATDecoder
from ..log.Log import Log
from .Algorithm import Algorithm

# Define a simple TimeoutException in case one is needed.
class TimeoutException(Exception):
    pass

class RCPSPAlgorithm(Algorithm):
    def __init__(self, project, bcc_mode):
        """
        Initializes the RCPSP algorithm with the given project and mode.
        
        :param project: A Project instance.
        :param bcc_mode: Boolean flag to select the resource encoding mode.
        """
        super().__init__(project)
        self.bcc_mode = bcc_mode
        self.encoder = None
        self.decoder = None
        self.solver = None
        self.encode_time_start = 0
        self.encode_time_end = 0

    def calculate(self):
        """
        Main method to run the RCPSP algorithm.
        It initializes the solver, encodes the project constraints,
        and then uses a bisection method to find the minimal project duration.
        """
        self.solver = self.init_solver()
        patch_solver_count_clauses(self.solver)

        min_time = self.get_min_time(self.project.get_activities()) - 1
        max_time = self.get_max_time(self.project.get_activities())
        if max_time > 0:
            self.encoder = SATEncoder.get_encoder()
            Log.d("Encoding starts...")
            print("Encoding starts...")
            self.encode_time_start = int(time.time() * 1000)
            self.encoder.encode(self.solver, self.project, max_time, self.bcc_mode)
            self.encode_time_end = int(time.time() * 1000)
            self.decoder = SATDecoder.get_decoder()
            try:
                self.solve_problem(min_time, max_time)
            except TimeoutException:
                self.reset_algorithm("TimeoutException")
            except MemoryError:
                self.reset_algorithm("OutOfMemoryError")
        else:
            Log.i("No encoding necessary! Project duration: " + str(max_time))
            print("No encoding necessary! Project duration: " + str(max_time))
            Log.write_log(self.project.get_name() +
                          " - No encoding necessary. Minimal project duration: 0")
            print(self.project.get_name() +
                  " - No encoding necessary. Minimal project duration: 0")
        self.reset_algorithm()

    def set_mode(self, bcc_mode):
        """Sets the resource encoding mode."""
        self.bcc_mode = bcc_mode

    def solve_problem(self, min_time, max_time):
        """
        Uses a bisection method on the time horizon to find a minimal
        satisfiable project duration.
        
        :param min_time: The lower bound on the project duration.
        :param max_time: The upper bound on the project duration.
        :raises TimeoutException: if the solver times out.
        """
        Log.d("Search algorithm started ...")
        print("Search algorithm started ...")
        initial_max_time = max_time
        solver = self.solver  # the PySAT solver instance
        sat = False
        sat_time_start = int(time.time() * 1000)
        print("max_time", max_time)
        while max_time - min_time > 1:
            mid_time = self.get_mid_time(min_time, max_time)
            # encoder.get_assumptions() should return a list of integer literals.
            assumptions = self.encoder.get_assumptions(mid_time, initial_max_time)
            sat = solver.solve(assumptions=assumptions)
            if sat:
                max_time = mid_time
            else:
                min_time = mid_time
        sat_time_end = int(time.time() * 1000)
        
        if sat:
            sat = "SAT"
            print(sat)
            model = solver.get_model()
            self.decoder.decode(self.project, model)
            Log.i("Project duration: " + str(max_time))
            print("Project duration: " + str(max_time))
        else:
            unsat = "UNSAT"
            print(unsat)
            last_sat_solution = self.solve_problem_for_initial_max_time(initial_max_time, solver)
            if last_sat_solution is not None:
                self.decoder.decode(self.project, last_sat_solution)
                Log.i("Project duration: " + str(initial_max_time))
                print("Project duration: " + str(initial_max_time))
        
        if psutil is not None:
            process = psutil.Process(os.getpid())
            mem_mb = process.memory_info().rss / (1024 * 1024)
        else:
            mem_mb = 0
        
        Log.write_log(
            self.project.get_name() + ";" +
            str(self.encode_time_end - self.encode_time_start) + " ms;" +
            str(sat_time_end - sat_time_start) + " ms;" +
            str(mem_mb) + " mb"
        )
        print(
            self.project.get_name() + ";" +
            str(self.encode_time_end - self.encode_time_start) + " ms;" +
            str(sat_time_end - sat_time_start) + " ms;" +
            str(mem_mb) + " mb"
        )
        Log.i("Done")
        print("Done")

    def init_solver(self):
        """
        Initializes the SAT solver.
        
        :return: An instance of a PySAT solver.
        """
        # Note: Minisat22 from python-sat does not support a built-in timeout.
        solver = Glucose3()
        return solver

    def get_min_time(self, activities):
        """
        Computes a lower bound for the project duration based on the activities.
        
        :param activities: A list of Activity objects.
        :return: An integer lower bound on project duration.
        """
        min_time_over_duration = 0
        min_time_over_early_end = 0
        for activity in activities:
            duration = activity.get_duration()
            early_end = int(activity.get_early_end_date())
            if duration > min_time_over_duration:
                min_time_over_duration = duration
            elif early_end > min_time_over_early_end:
                min_time_over_early_end = early_end
        return max(min_time_over_duration, min_time_over_early_end)

    def get_max_time(self, activities):
        """
        Computes an upper bound for the project duration by summing activity durations.
        
        :param activities: A list of Activity objects.
        :return: The total duration as an integer.
        """
        max_time = 0
        for activity in activities:
            max_time += activity.get_duration()
        return max_time

    def get_mid_time(self, min_time, max_time):
        """
        Computes the midpoint between min_time and max_time.
        
        :param min_time: The lower bound.
        :param max_time: The upper bound.
        :return: The midpoint (integer).
        """
        return (min_time + max_time) // 2

    def solve_problem_for_initial_max_time(self, max_time, solver):
        """
        If the bisection search did not succeed, this method checks for a solution
        at the initial maximum time.
        
        :param max_time: The initial maximum time.
        :param solver: The solver instance.
        :return: A solution model (list of integers) or None.
        :raises TimeoutException: if the solver times out.
        """
        sat = solver.solve()
        if sat:
            return solver.get_model()
        return None

    def reset_algorithm(self, cause=None):
        """
        Resets the algorithm's solver and encoder. If a cause is provided,
        it is logged.
        
        :param cause: Optional string describing why the reset is occurring.
        """
        if cause:
            Log.write_log(self.project.get_name() + " - " + cause)
            print(self.project.get_name() + " - " + cause)
        if self.solver is not None:
            self.solver.delete()  # Free resources held by the PySAT solver.
        if self.encoder is not None:
            self.encoder.reset()
    
def patch_solver_count_clauses(solver):
    # Initialize a counter attribute on the solver.
    solver._clause_count = 0
    original_add_clause = solver.add_clause

    def new_add_clause(clause):
        solver._clause_count += 1
        return original_add_clause(clause)
    
    solver.add_clause = new_add_clause
