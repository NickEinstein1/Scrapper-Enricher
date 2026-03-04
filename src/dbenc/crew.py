from crewai import Agent, Crew, Process, Task
from src.dbenc.tools.supabase_tool import SupabaseTool
from src.dbenc.tools.scraping_tool import ScrapingTool
from src.dbenc.tools.geocoding_tool import GeocodingTool
import logging
import yaml
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchoolEnrichmentCrew:
    def __init__(self, agents_file: str = "src/dbenc/config/agents.yaml", tasks_file: str = "src/dbenc/config/tasks.yaml", use_mock: bool = True, timeout: int = 60):
        self.timeout = timeout
        # Load YAML configurations
        try:
            logger.info(f"Loading agents from {agents_file}")
            with open(agents_file, 'r') as f:
                self.agents_config = yaml.safe_load(f)
            logger.info(f"Loading tasks from {tasks_file}")
            with open(tasks_file, 'r') as f:
                self.tasks_config = yaml.safe_load(f)
            logger.info("YAML configurations loaded successfully")
        except Exception as e:
            logger.error(f"Error loading YAML configurations: {e}")
            import os
            logger.info(f"Current working directory: {os.getcwd()}")
            raise

        # Initialize tools
        logger.info(f"Initializing tools with mock_mode={use_mock}")
        self.supabase_tool = SupabaseTool()
        self.scraping_tool = ScrapingTool(mock_mode=use_mock)
        self.geocoding_tool = GeocodingTool(mock_mode=use_mock)

        # Initialize agents
        logger.info("Creating agents")
        self._researcher_agent = None
        self._scraper_agent = None
        self._geocoder_agent = None
        self._reporter_agent = None

    def researcher(self) -> Agent:
        if self._researcher_agent is None:
            config = self.agents_config['researcher']
            # Optimize backstory to reduce context size
            backstory = config['backstory'].split('\n\n')[0]  # Just keep the first paragraph

            from langchain.chat_models import ChatOpenAI
            llm = ChatOpenAI(model="gpt-3.5-turbo")
            self._researcher_agent = Agent(
                role=config['role'],
                goal=config['goal'],
                backstory=backstory,
                tools=[self.supabase_tool],
                verbose=True,
                llm=llm  # Use a LangChain ChatOpenAI instance instead of a string
            )
            # Test the tool to ensure it's working
            try:
                test_result = self.supabase_tool._run(action="get_schools", limit=1)
                logger.info(f"Supabase tool test: {test_result is not None}")
            except Exception as e:
                logger.error(f"Error testing supabase_tool: {e}")
            logger.info("Researcher agent created")
        return self._researcher_agent

    def scraper(self) -> Agent:
        if self._scraper_agent is None:
            config = self.agents_config['scraper']
            # Optimize backstory to reduce context size
            backstory = config['backstory'].split('\n\n')[0]  # Just keep the first paragraph

            from langchain.chat_models import ChatOpenAI
            llm = ChatOpenAI(model="gpt-3.5-turbo")
            self._scraper_agent = Agent(
                role=config['role'],
                goal=config['goal'],
                backstory=backstory,
                tools=[self.scraping_tool],
                verbose=True,
                llm=llm  # Use a LangChain ChatOpenAI instance instead of a string
            )
            # Test the tool to ensure it's working
            try:
                test_result = self.scraping_tool._run(action="help")
                logger.info(f"Scraping tool test: {test_result is not None}")
            except Exception as e:
                logger.error(f"Error testing scraping_tool: {e}")
            logger.info("Scraper agent created")
        return self._scraper_agent

    def geocoder(self) -> Agent:
        if self._geocoder_agent is None:
            config = self.agents_config['geocoder']
            # Optimize backstory to reduce context size
            backstory = config['backstory'].split('\n\n')[0]  # Just keep the first paragraph

            from langchain.chat_models import ChatOpenAI
            llm = ChatOpenAI(model="gpt-3.5-turbo")
            self._geocoder_agent = Agent(
                role=config['role'],
                goal=config['goal'],
                backstory=backstory,
                tools=[self.geocoding_tool],
                verbose=True,
                llm=llm  # Use a LangChain ChatOpenAI instance instead of a string
            )
            # Test the tool to ensure it's working
            try:
                test_result = self.geocoding_tool._run(action="help")
                logger.info(f"Geocoding tool test: {test_result is not None}")
            except Exception as e:
                logger.error(f"Error testing geocoding_tool: {e}")
            logger.info("Geocoder agent created")
        return self._geocoder_agent

    def reporter(self) -> Agent:
        if self._reporter_agent is None:
            config = self.agents_config['reporter']
            # Optimize backstory to reduce context size
            backstory = config['backstory'].split('\n\n')[0]  # Just keep the first paragraph

            from langchain.chat_models import ChatOpenAI
            llm = ChatOpenAI(model="gpt-3.5-turbo")
            self._reporter_agent = Agent(
                role=config['role'],
                goal=config['goal'],
                backstory=backstory,
                tools=[self.supabase_tool],
                verbose=True,
                llm=llm  # Use a LangChain ChatOpenAI instance instead of a string
            )
            # Test the tool to ensure it's working
            try:
                test_result = self.supabase_tool._run(action="help")
                logger.info(f"Supabase tool (reporter) test: {test_result is not None}")
            except Exception as e:
                logger.error(f"Error testing supabase_tool (reporter): {e}")
            logger.info("Reporter agent created")
        return self._reporter_agent

    def research_task(self, input_data: Dict[str, Any]) -> Task:
        config = self.tasks_config['research_task']
        # Format the context properly
        context_item = {
            "description": "School data to enrich",
            "expected_output": "Enriched school data",
            "data": input_data
        }
        context_list = [context_item]
        logger.info(f"Research task context: {context_list}")
        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=self.researcher(),
            context=context_list
        )

    def scraping_task(self) -> Task:
        config = self.tasks_config['scraping_task']
        # Format the context properly
        context_item = {
            "description": "School data from research",
            "expected_output": "Scraped school data",
            "data": {"schools": []},  # Will be populated by task_callback
            "previous_task_output": []  # Will be populated by task_callback
        }
        context_list = [context_item]
        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=self.scraper(),
            context=context_list
        )

    def geocoding_task(self) -> Task:
        config = self.tasks_config['geocoding_task']
        # Format the context properly
        context_item = {
            "description": "School data from scraping",
            "expected_output": "Geocoded school data",
            "data": {"schools": []},  # Will be populated by task_callback
            "previous_task_output": []  # Will be populated by task_callback
        }
        context_list = [context_item]
        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=self.geocoder(),
            context=context_list
        )

    def reporting_task(self) -> Task:
        config = self.tasks_config['reporting_task']
        # Format the context properly
        context_item = {
            "description": "School data from geocoding",
            "expected_output": "Final report on enriched school data",
            "data": {"schools": []},  # Will be populated by task_callback
            "previous_task_output": [],  # Will be populated by task_callback
            "task_history": []  # Will be populated by task_callback
        }
        context_list = [context_item]
        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=self.reporter(),
            context=context_list
        )

    def run_crew(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Log the input data
        logger.info(f"Running crew with {len(input_data.get('schools', []))} schools")

        # Validate input data
        if not input_data.get('schools'):
            logger.error("No schools provided in input_data")
            return {"error": "No schools provided in input_data"}

        # Validate school data
        for i, school in enumerate(input_data.get('schools', [])):
            if not school.get('school_id'):
                logger.warning(f"School at index {i} is missing school_id, skipping")
                continue
            if not school.get('school_name'):
                logger.warning(f"School with ID {school.get('school_id')} is missing school_name")

        # Add current year to input data for context
        from datetime import datetime
        input_data['current_year'] = str(datetime.now().year)

        # Create a callback to track task outputs for context sharing
        task_outputs = []
        tasks_by_name = {}

        def task_callback(task_output):
            logger.info(f"Task callback received: {task_output}")
            task_description = task_output.description

            # Handle different versions of CrewAI TaskOutput
            if hasattr(task_output, 'exported_output'):
                # CrewAI 0.28.0
                output = task_output.exported_output
            elif hasattr(task_output, 'raw'):
                # Earlier versions
                output = task_output.raw
            else:
                # Fallback
                output = str(task_output)
                logger.warning(f"Could not find 'exported_output' or 'raw' attribute in task_output: {task_output}")

            logger.info(f"Task {task_description[:50]}... completed with output: {output[:100]}..." if isinstance(output, str) and len(output) > 100 else f"Task {task_description[:50]}... completed with output: {output}")

            # Determine which task this is based on the description
            current_task_name = None
            if "research" in task_description.lower():
                current_task_name = "research_task"
            elif "scraping" in task_description.lower():
                current_task_name = "scraping_task"
            elif "geocoding" in task_description.lower():
                current_task_name = "geocoding_task"
            elif "reporting" in task_description.lower():
                current_task_name = "reporting_task"

            logger.info(f"Identified task as: {current_task_name}")

            # Add to task history
            task_outputs.append({"task": current_task_name, "output": output})

            # Store the task output for context sharing
            if current_task_name:
                tasks_by_name[current_task_name] = output

                # Update context for subsequent tasks based on the completed task
                if current_task_name == "research_task":
                    # Update scraping task with research output
                    for i, task in enumerate(crew.tasks):
                        if "scraping" in task.description.lower():
                            logger.info("Updating scraping task context with research output")
                            try:
                                # In CrewAI 0.28.0, we need to handle context updates differently
                                # Create a new context list with updated items
                                new_context = []
                                for context_item in task.context:
                                    # Create a deep copy to avoid modifying the original
                                    new_item = {}
                                    # Handle different types of context_item
                                    if hasattr(context_item, 'items'):
                                        for key, value in context_item.items():
                                            new_item[key] = value
                                    else:
                                        # If context_item is not a dict-like object, copy it as is
                                        new_item = context_item

                                    # Add the new data
                                    if isinstance(new_item, dict):
                                        new_item["previous_task_output"] = output
                                        new_item["data"] = input_data
                                    new_context.append(new_item)

                                # Update the task's context directly
                                task.context = new_context
                                logger.info("Successfully updated scraping task context")
                            except Exception as e:
                                logger.error(f"Error updating scraping task context: {e}")
                            break

                elif current_task_name == "scraping_task":
                    # Update geocoding task with scraping output
                    for i, task in enumerate(crew.tasks):
                        if "geocoding" in task.description.lower():
                            logger.info("Updating geocoding task context with scraping output")
                            try:
                                # In CrewAI 0.28.0, we need to handle context updates differently
                                # Create a new context list with updated items
                                new_context = []
                                for context_item in task.context:
                                    # Create a deep copy to avoid modifying the original
                                    new_item = {}
                                    # Handle different types of context_item
                                    if hasattr(context_item, 'items'):
                                        for key, value in context_item.items():
                                            new_item[key] = value
                                    else:
                                        # If context_item is not a dict-like object, copy it as is
                                        new_item = context_item

                                    # Add the new data
                                    if isinstance(new_item, dict):
                                        new_item["previous_task_output"] = output
                                        new_item["data"] = input_data
                                    new_context.append(new_item)

                                # Update the task's context directly
                                task.context = new_context
                                logger.info("Successfully updated geocoding task context")
                            except Exception as e:
                                logger.error(f"Error updating geocoding task context: {e}")
                            break

                elif current_task_name == "geocoding_task":
                    # Update reporting task with geocoding output and task history
                    for i, task in enumerate(crew.tasks):
                        if "reporting" in task.description.lower():
                            logger.info("Updating reporting task context with geocoding output and task history")
                            try:
                                # In CrewAI 0.28.0, we need to handle context updates differently
                                # Create a new context list with updated items
                                new_context = []
                                for context_item in task.context:
                                    # Create a deep copy to avoid modifying the original
                                    new_item = {}
                                    # Handle different types of context_item
                                    if hasattr(context_item, 'items'):
                                        for key, value in context_item.items():
                                            new_item[key] = value
                                    else:
                                        # If context_item is not a dict-like object, copy it as is
                                        new_item = context_item

                                    # Add the new data
                                    if isinstance(new_item, dict):
                                        new_item["previous_task_output"] = output
                                        new_item["data"] = input_data
                                        new_item["task_history"] = task_outputs
                                    new_context.append(new_item)

                                # Update the task's context directly
                                task.context = new_context
                                logger.info("Successfully updated reporting task context")
                            except Exception as e:
                                logger.error(f"Error updating reporting task context: {e}")
                            break

        # Create a crew with all necessary agents and tasks
        # This ensures all tools (scraping, geocoding, supabase) are used properly
        logger.info("Creating Crew instance with agents and tasks")
        try:
            agents = [
                self.researcher(),  # For database research
                self.scraper(),     # For web scraping
                self.geocoder(),    # For geocoding
                self.reporter()     # For reporting and updating
            ]
            logger.info(f"Created {len(agents)} agents successfully")

            tasks = [
                self.research_task(input_data),  # Find schools needing enrichment
                self.scraping_task(),           # Scrape data from websites
                self.geocoding_task(),          # Add geographic coordinates
                self.reporting_task()           # Update database and report
            ]
            logger.info(f"Created {len(tasks)} tasks successfully")

            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.sequential,
                verbose=True,
                task_callback=task_callback
            )
            logger.info("Crew instance created successfully")
        except Exception as crew_error:
            logger.error(f"Error creating Crew instance: {crew_error}")
            import traceback
            logger.error(f"Crew creation traceback: {traceback.format_exc()}")
            raise

        # Log the crew configuration
        logger.info(f"Created crew with {len(crew.agents)} agents and {len(crew.tasks)} tasks")
        logger.info(f"Agents: {[agent.role for agent in crew.agents]}")
        logger.info(f"Tasks: {[task.description[:50] + '...' for task in crew.tasks]}")

        # Set a timeout to avoid excessive API usage with improved cleanup
        try:
            logger.info("Starting crew kickoff with timeout")
            # Use a timeout to prevent excessive API calls
            import concurrent.futures
            import time

            result = None
            max_time = self.timeout  # Use the timeout from the constructor
            max_retries = 2  # Number of retries if the crew execution fails

            for retry in range(max_retries + 1):
                try:
                    # Run the crew with a timeout
                    logger.info("Starting crew kickoff with ThreadPoolExecutor")
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        try:
                            logger.info("Submitting crew.kickoff to executor")
                            future = executor.submit(crew.kickoff)
                            logger.info("Waiting for result with timeout")
                            result = future.result(timeout=max_time)
                            logger.info(f"Got result: {type(result)}")
                        except Exception as inner_e:
                            logger.error(f"Inner exception in executor: {inner_e}")
                            logger.error(f"Inner exception type: {type(inner_e)}")
                            import traceback
                            logger.error(f"Inner exception traceback: {traceback.format_exc()}")
                            raise
                    # If we get here, the crew executed successfully
                    break
                except concurrent.futures.TimeoutError:
                    logger.warning(f"Crew execution timed out after {max_time} seconds (attempt {retry + 1}/{max_retries + 1})")
                    if retry < max_retries:
                        logger.info(f"Retrying in 5 seconds...")
                        time.sleep(5)  # Wait before retrying
                    else:
                        result = {"error": f"Timeout after {max_time} seconds (all {max_retries + 1} attempts failed)"}
                except Exception as e:
                    logger.error(f"Error in crew kickoff (attempt {retry + 1}/{max_retries + 1}): {e}")
                    if retry < max_retries:
                        logger.info(f"Retrying in 5 seconds...")
                        time.sleep(5)  # Wait before retrying
                    else:
                        result = {"error": f"Error in crew kickoff: {str(e)} (all {max_retries + 1} attempts failed)"}

            # Log the result
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Crew execution failed: {result['error']}")
            else:
                logger.info("Crew execution completed successfully")

            return result
        except Exception as e:
            logger.error(f"Error in run_crew: {e}")
            return {"error": str(e)}

# Optional: Test the loading
if __name__ == "__main__":
    crew = SchoolEnrichmentCrew()
    logger.info("Agents config loaded: %s", crew.agents_config)
    logger.info("Tasks config loaded: %s", crew.tasks_config)