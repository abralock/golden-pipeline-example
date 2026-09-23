plugins {
    java
    jacoco
    checkstyle
}

group = "com.example"
version = "0.0.0" // real version = git tag created by semantic-release

repositories {
    mavenCentral() // corporate: replace with the Artifactory/Nexus mirror (or set it in an init script)
}

dependencies {
    testImplementation(platform("org.junit:junit-bom:5.11.4"))
    testImplementation("org.junit.jupiter:junit-jupiter")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.withType<JavaCompile>().configureEach {
    options.release = 21 // JDK 21 service
}

// Lint: platform checkstyle baseline (complexity <= 8), zero warnings allowed
checkstyle {
    toolVersion = "10.21.4"
    configFile = file("config/checkstyle.xml")
    maxWarnings = 0
}

tasks.test {
    useJUnitPlatform()
    finalizedBy(tasks.jacocoTestReport)
}

// Coverage: XML report -> build/reports/jacoco/test/jacocoTestReport.xml
tasks.jacocoTestReport {
    dependsOn(tasks.test)
    reports {
        xml.required = true
        html.required = false
    }
}
