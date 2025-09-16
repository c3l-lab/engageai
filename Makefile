synth: ## Synthesize the entire CDK stack
	# We need to run 'build' as a prerequisite for 'synth' to ensure that CDK has all the necessary artifacts.
	cd cdk && $(MAKE) synth

run: 
	cd modules/c3l_agents_orchestrator && make run


# We'll try to run tests / linting / formatting jobs in parallel batches of 8
MAKEFLAGS += --jobs=8

# These are the directories that we want to run our install / lint / test / format commands in
MODULES = $(wildcard modules/* cdk)

# This is a bit of 'make' wizardry that runs the 'install' target in each of the MODULES directories
# But it lets us run them all in parallel, which is heaps faster
install-modules := $(addprefix install-, $(MODULES))
${install-modules}: install-%:
	cd $* && $(MAKE) install
install: ${install-modules} ## Install all dependencies in all modules

lint-modules := $(addprefix lint-, $(MODULES))
${lint-modules}: lint-%:
	cd $* && $(MAKE) lint
lint: ${lint-modules} ## Lint all our code

test-modules := $(addprefix test-, $(MODULES))
${test-modules}: test-%:
	cd $* && $(MAKE) test
test: ${test-modules} ## Run all our tests
