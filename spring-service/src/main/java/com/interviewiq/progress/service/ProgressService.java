package com.interviewiq.progress.service;

import com.interviewiq.progress.model.StudyProgress;
import com.interviewiq.progress.repository.ProgressRepository;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;

import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ProgressService {

    private final ProgressRepository progressRepository;


    // ===============================
    // CONSTRUCTOR INJECTION
    // ===============================

    public ProgressService(
            ProgressRepository progressRepository
    ) {

        this.progressRepository = progressRepository;
    }


    // ===============================
    // BEAN LIFE CYCLE
    // ===============================

    @PostConstruct
    public void init() {

        System.out.println(
                "ProgressService Bean Initialized"
        );
    }


    @PreDestroy
    public void destroy() {

        System.out.println(
                "ProgressService Bean Destroyed"
        );
    }


    // ===============================
    // GET USER PROGRESS
    // ===============================

    public List<StudyProgress> getUserProgress(
            String userId
    ) {

        return progressRepository
                .findByUserId(userId);
    }


    // ===============================
    // SAVE OR UPDATE PROGRESS
    // ===============================

    public StudyProgress saveOrUpdateProgress(
            StudyProgress progress
    ) {

        return progressRepository
                .findByUserIdAndTopicName(
                        progress.getUserId(),
                        progress.getTopicName()
                )
                .map(existingProgress -> {

                    existingProgress.setCompleted(
                            progress.getCompleted()
                    );

                    return progressRepository.save(
                            existingProgress
                    );
                })
                .orElseGet(() ->
                        progressRepository.save(progress)
                );
    }


    // ===============================
    // COMPLETED TOPIC COUNT
    // ===============================

    public long getCompletedTopicCount(
            String userId
    ) {

        return progressRepository
                .findByUserId(userId)
                .stream()
                .filter(progress ->
                        Boolean.TRUE.equals(
                                progress.getCompleted()
                        )
                )
                .count();
    }


    // ===============================
    // DELETE PROGRESS
    // ===============================

    public void deleteProgress(
            Long id
    ) {

        progressRepository.deleteById(id);
    }
}
