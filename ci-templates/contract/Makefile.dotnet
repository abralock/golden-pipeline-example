# Makefile contract - .NET starter (C#, .NET 8 LTS; .NET 10 LTS = change TargetFramework + build image).
# Test projects need: Microsoft.NET.Test.Sdk, xunit (or NUnit/MSTest), coverlet.collector, JunitXml.TestLogger
# Repo needs: .config/dotnet-tools.json with dotnet-reportgenerator-globaltool (merges per-project coverage)
# Complexity limit: CA1502 enabled in .editorconfig + CodeMetricsConfig.txt ("CA1502: 8"),
#   and TreatWarningsAsErrors in Directory.Build.props (see samples/dotnet-service).
# Build image: the official SDK image has no `make` - the platform build-dotnet image adds it.
# Corporate networks: point NuGet at Artifactory/Nexus with a nuget.config in the build image.
CONFIG ?= Release

.PHONY: setup lint test coverage build

setup:
	dotnet restore
	dotnet tool restore

lint:
	dotnet format --verify-no-changes --no-restore
	dotnet build --no-restore -c $(CONFIG)

test:
	dotnet test --no-restore -c $(CONFIG)

coverage:
	rm -rf reports && mkdir -p reports
	dotnet test --no-restore -c $(CONFIG) \
	  --logger "junit;LogFilePath=$(CURDIR)/reports/junit-{assembly}.xml" \
	  --collect "XPlat Code Coverage" --results-directory reports/raw \
	  -- DataCollectionRunSettings.DataCollector.Configuration.Format=cobertura
	dotnet tool run reportgenerator "-reports:reports/raw/**/coverage.cobertura.xml" \
	  -targetdir:reports/merged -reporttypes:Cobertura
	cp reports/merged/Cobertura.xml reports/coverage.xml

build:
	dotnet publish src/Pricing/Pricing.csproj -c $(CONFIG) --no-restore -o dist
